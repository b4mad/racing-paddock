import csv
import json
import logging
from io import BytesIO
from pathlib import Path

from django.core.management.base import BaseCommand
from openai import OpenAI
from pydub import AudioSegment

# from telemetry.factories import DriverFactory
from telemetry.management.commands.rbr_roadbook import NoteMapper, Roadbook
from telemetry.models import Game, Landmark, TrackGuide


class Command(BaseCommand):
    help = "Load data"

    def add_arguments(self, parser):
        parser.add_argument("--landmarks", action="store_true")
        parser.add_argument("--landmarks-rbr", nargs="?", type=str)
        parser.add_argument("--track-name", nargs="?", type=str, help="Optional track name for --landmarks-rbr")
        parser.add_argument("--tts", action="store_true")
        parser.add_argument("--track-guide", nargs="?", type=str)
        parser.add_argument("--session", action="store_true")

    def handle(self, *args, **options):
        if options["landmarks"]:
            self.landmarks()
        if options["track_guide"]:
            self.trackguide(options["track_guide"])
        if options["tts"]:
            self.generate_tts()
        if options["landmarks_rbr"]:
            self.rbr_roadbook(options["landmarks_rbr"], options["track_name"])
        if options["session"]:
            self.session()

    # def session(self):
    #     mqtt = MqttPublisher()
    #     session_id = "1703706617"
    #     session_df = get_session_df(session_id)

    #     for index, row in session_df.iterrows():
    #         row = row.to_dict()
    #         mqtt.publish_df_dict(row)

    def generate_tts(self):
        client = OpenAI()

        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            response_format="mp3",
            input="Today is a wonderful day to build something people love!",
        )

        # Store the output in a buffer
        buffer = BytesIO(response.audio)

        # Load mp3 from buffer
        audio = AudioSegment.from_file(buffer, format="mp3")

        # Convert mp3 to wav
        audio.export("speech.wav", format="wav")

    def trackguide(self, filename):
        # https://simracing.wiki/BMW_M4_GT4_(iRacing)
        # https://iracing.fandom.com/wiki/BMW_M4_GT4
        # https://ams2cars.info/gt-sports/gt4/m4-gt4/
        # https://virtualracingschool.convertri.com/vrs-qrtm-download/
        # https://virtualracingschool.com/wp-content/uploads/BMW-12.0-GT4-Monza.pdf

        # filename without extension and leading path
        basename = Path(filename).stem
        (game_name, car_name, track_name) = basename.split("--")

        game = Game.objects.filter(name=game_name).first()
        track = game.tracks.filter(name=track_name).first()
        car = game.cars.filter(name=car_name).first()

        logging.debug(f"Track Guide for {game} - {track} - {car}")

        track_guide = TrackGuide.objects.get_or_create(track=track, car=car)[0]
        # track_guide.name = "BMW GT4 at Monza GP S1 2022 by Pablo Lopez"
        # track_guide.description = "https://virtualracingschool.com/wp-content/uploads/BMW-12.0-GT4-Monza.pdf"
        track_guide.save()

        track_guide.notes.all().delete()
        # data_file = Path(__file__).parent / "track_guide.csv"
        data_file = Path(filename)
        with open(data_file) as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # notes.append(row)
                data = row
                data["priority"] = int(data["priority"] or "0")

                if not data["at"].strip():
                    data.pop("at")

                if not row["segment"].strip():
                    logging.debug(f"!!! segement empty - skip line: '{row}' for track {track}")
                    continue

                # check if segment is just numbers
                if row["segment"].isnumeric():
                    data["segment"] = int(data["segment"])
                else:
                    # find the landmark
                    data["landmark"] = track.landmarks.filter(name=row["segment"].strip()).first()
                    if not data["landmark"]:
                        logging.debug(f"!!! Landmark not found: '{row['segment']}' for track {track}")
                        exit(1)
                    # unset segment
                    data.pop("segment")
                logging.debug(data)
                track_guide.notes.create(**data)

    def rbr_roadbook_load_data(self, path, track, mapper):
        # Open the path and get the file with the latest modified date
        latest_file = max(Path(path).glob("*.ini"), key=lambda f: f.stat().st_mtime)
        logging.info(f"Latest file: {latest_file}")
        book = Roadbook(latest_file)
        # remove all existing notes
        Landmark.objects.filter(track=track, from_cc=True).delete()

        previous_turn_distance = 0
        turns = []

        # First pass: collect all turns
        for note_id, note in book.notes.items():
            mapped_note = mapper.map(note.type)
            if mapped_note and mapped_note["category"] == "CORNERS":
                turns.append((note.distance, mapped_note["name"]))

        # Second pass: create landmarks including segments
        for i, (distance, name) in enumerate(turns):
            # Create turn landmark
            logging.debug(f"Creating turn landmark {name}")
            Landmark.objects.create(name=name, start=distance, track=track, kind=Landmark.KIND_TURN, from_cc=True)

            # Create segment landmark (except before the first turn)
            if i == 0:
                segment_start = 0
                next_turn = turns[i + 1]
                next_turn_distance = next_turn[0]
                segment_end = (distance + next_turn_distance) / 2
            elif i == len(turns) - 1:
                segment_end = track.length
                previous_turn = turns[i - 1]
                previous_turn_distance = previous_turn[0]
                segment_start = (previous_turn_distance + distance) / 2
            else:
                previous_turn = turns[i - 1]
                next_turn = turns[i + 1]
                previous_turn_distance = previous_turn[0]
                next_turn_distance = next_turn[0]
                segment_start = (previous_turn_distance + distance) / 2
                segment_end = (distance + next_turn_distance) / 2

            segment_name = f"Segment {i}"
            logging.debug(f"Creating segment landmark {segment_name}")
            Landmark.objects.create(
                name=segment_name,
                start=segment_start,
                end=segment_end,
                track=track,
                kind=Landmark.KIND_SEGMENT,
                from_cc=True,
            )

        # Create other landmarks (non-turns)
        for note_id, note in book.notes.items():
            mapped_note = mapper.map(note.type)
            if mapped_note and mapped_note["category"] != "CORNERS":
                name = mapped_note["name"]
                kind = Landmark.KIND_MISC
                logging.debug(f"Creating misc landmark {name}")
                Landmark.objects.create(name=name, start=note.distance, track=track, kind=kind, from_cc=True)

    def rbr_roadbook(self, filename, filter_track_name=None):
        # get all tracks for Richard Burns Rally
        tracks = Game.objects.filter(name="Richard Burns Rally").first().tracks.all()
        mapper = NoteMapper()

        for track in tracks:
            # logging.debug(track)
            # see if a directory exists for the track
            track_name = track.name
            if filter_track_name and track_name != filter_track_name:
                continue

            # translate all umlaute to ascii
            track_name = track_name.replace("ä", "a").replace("ö", "o").replace("ü", "u")
            track_name = track_name.replace(".", "_").replace("'", "_").replace("é", "e")
            roadbook_path = Path(filename) / track_name
            if roadbook_path.exists():
                self.rbr_roadbook_load_data(roadbook_path, track, mapper)
            else:
                # try to append ' BTB' to the track name
                roadbook_path = Path(filename) / f"{track_name} BTB"
                if roadbook_path.exists():
                    self.rbr_roadbook_load_data(roadbook_path, track, mapper)
                else:
                    logging.debug(f"No roadbook found for {track}")

    def landmarks(self):
        # Load track landmarks data
        data_file = Path(__file__).parent / "trackLandmarksData.json"
        with open(data_file) as f:
            landmarks_data = json.load(f)

        # delete all landmarks
        # Landmark.objects.all().delete()

        games_keys = {
            "acTrackNames": Game.objects.filter(name="Assetto Corsa (64 bit)").first(),
            "ams2TrackName": Game.objects.filter(name="Automobilista 2").first(),
            "irTrackName": Game.objects.filter(name="iRacing").first(),
            "accTrackName": Game.objects.filter(name="Assetto Corsa Competizione").first(),
        }

        # Iterate over each track's landmarks
        for track_data in landmarks_data["TrackLandmarksData"]:
            for key, game in games_keys.items():
                if key in track_data:
                    track_names = track_data[key]
                    # if track_name is an array, iterate over each track name
                    if not isinstance(track_names, list):
                        track_names = [track_names]

                    for track_name in track_names:
                        if not track_name:
                            logging.debug(f"!!! Empty track name for {game}")
                            continue
                        track, created = game.tracks.get_or_create(name=track_name)
                        logging.debug(f"{game}: {track}")
                        if created:
                            logging.debug(f"!!! Created new track: {track}")

                        # Create or update landmarks
                        for landmark_data in track_data["trackLandmarks"]:
                            # Try to find existing landmark
                            landmark, created = Landmark.objects.get_or_create(
                                name=landmark_data["landmarkName"], track=track, kind=Landmark.KIND_TURN, from_cc=True
                            )
                            logging.debug(f"  {landmark}")

                            # Update fields if needed
                            landmark.start = landmark_data["distanceRoundLapStart"]
                            landmark.end = landmark_data["distanceRoundLapEnd"]
                            landmark.is_overtaking_spot = landmark_data["isCommonOvertakingSpot"]

                            landmark.save()

            # break

    # @transaction.atomic
    # def devel_data(self, *args, **kwargs):
    #     self.stdout.write("Deleting old data...")
    #     Driver.objects.all().delete()

    #     self.stdout.write("Creating new data...")
    #     people = []
    #     for _ in range(50):
    #         driver_factory = DriverFactory()
    #         people.append(driver_factory)
