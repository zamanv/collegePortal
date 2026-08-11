"""One-time upgrade helper for databases that already use the default user model.

When an existing database (auth_user + applied Django admin migrations) is
switched to a custom user model, ``manage.py migrate`` refuses to run:

    InconsistentMigrationHistory: Migration admin.0001_initial is applied
    before its dependency accounts.0001_initial.

Django refuses because it must render the already-applied admin/auth models
(which now reference ``accounts.user``) before ``accounts.0001`` exists in the
migration record.  This command breaks the deadlock deterministically:

1. Creates the ``accounts_user`` (+ groups, + user_permissions) tables using
   the real ``User`` model, producing exactly the schema the migration would.
2. Records ``accounts.0001_initial`` as applied.

Afterwards a normal ``python manage.py migrate`` can run: it copies the legacy
``auth_user`` rows (accounts/0002), creates ``AuditLog`` (0003), and upgrades
the faculty/student apps.

The command is idempotent and safe on fresh databases too (it no-ops when the
table or migration record already exists).
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder


class Command(BaseCommand):
    help = (
        "Create the accounts_user tables and record accounts.0001_initial as "
        "applied. Run once before `migrate` when upgrading an existing "
        "database to the custom user model."
    )

    def handle(self, *args, **options):
        from accounts.models import User

        recorder = MigrationRecorder(connection)

        # 1. Create the accounts_user (+ M2M) tables if they do not exist.
        user_table = User._meta.db_table
        if user_table not in connection.introspection.table_names():
            self.stdout.write(f"Creating {user_table} (+ M2M tables)...")
            with connection.schema_editor() as editor:
                editor.create_model(User)
        else:
            self.stdout.write(f"{user_table} already exists, skipping creation.")

        # 2. Record accounts.0001_initial as applied (if not already).
        applied = recorder.applied_migrations()
        if "0001_initial" not in applied.get("accounts", []):
            self.stdout.write("Recording accounts.0001_initial as applied...")
            recorder.record_applied("accounts", "0001_initial")
        else:
            self.stdout.write("accounts.0001_initial already recorded, skipping.")

        self.stdout.write(
            self.style.SUCCESS(
                "Done. Run `python manage.py migrate` to finish the upgrade "
                "(copies legacy users, creates AuditLog, upgrades profiles)."
            )
        )
