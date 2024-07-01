from django.test import TransactionTestCase

from b4mad_racing_website.models import Copilot
from telemetry.models import Coach, Driver
from telemetry.pitcrew.coach_copilots_no_history import CoachCopilotsNoHistory

from .utils import get_session_df, read_responses, save_responses


class TestCommentatorApp(TransactionTestCase):
    fixtures = [
        "game.json",
        "track.json",
        "car.json",
        "session.json",
        "sessiontype.json",
        "lap.json",
        "fastlap.json",
        "fastlapsegment.json",
        "driver.json",
        "coach.json",
        "trackguide.json",
        "trackguidenote.json",
        "landmark.json",
        "copilot.json",
        "copilotinstance.json",
        "profile.json",
        "user.json",
    ]
    maxDiff = None

    do_save_responses = True

    def test_commentator(self):
        session_id = "1703706617"
        driver = Driver.objects.get(name="durandom")
        coach = driver.coach
        coach.mode = Coach.MODE_COPILOTS
        coach.save()

        # Delete all Copilots where the slug is not "commentator"
        Copilot.objects.exclude(slug="commentator").delete()

        copilot_count = Copilot.objects.count()
        self.assertEqual(copilot_count, 1)

        coach = CoachCopilotsNoHistory(coach)

        session_df = get_session_df(session_id, measurement="laps_cc", bucket="racing")

        row = session_df.iloc[0].to_dict()
        topic = row["topic"].replace("Jim", "durandom")

        captured_responses = []
        for index, row in session_df.iterrows():
            row = row.to_dict()
            notify_topic = topic
            if index == 0:
                notify_topic = topic.replace("/Race", "/NewSession")
            response = coach.notify(notify_topic, row, row["_time"])
            if response:
                captured_responses.append((row["DistanceRoundTrack"], response))

        responses_file = "test_copilot_commentator"
        if self.do_save_responses:
            save_responses(captured_responses, responses_file)
        expected_responses = read_responses(responses_file)

        self.assertEqual(captured_responses, expected_responses)

        # assert that responses are not empty
        self.assertTrue(captured_responses)
