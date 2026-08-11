from django.core.management.base import BaseCommand

from faculty.services import cleanup_expired


class Command(BaseCommand):
    help = "Remove expired QR attendance tokens and auto-close stale sessions."

    def handle(self, *args, **options):
        tokens, sessions = cleanup_expired()
        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {tokens} expired token(s) and closed {sessions} stale session(s)."
            )
        )
