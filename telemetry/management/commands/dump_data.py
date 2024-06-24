from django.core.management.base import BaseCommand

from telemetry.models import Telemetry


class Command(BaseCommand):
    help = "Dump data"

    def add_arguments(self, parser):
        parser.add_argument("--session", action="store_true")

    def handle(self, *args, **options):
        if options["session"]:
            self.session()

    def session(self):
        session_id = "1703706617"
        # find the Telemetry object with the session_id
        telemetry_data = Telemetry.objects.filter(session_id_telemetry=session_id).values("throttle")
        telemetry_list = list(telemetry_data)

        print(telemetry_list)
        # print the telemetry object
