"""
Data migration: move existing ``auth_user`` rows into ``accounts_user``.

This is the safety net for upgrading an existing database to the custom user
model.  It preserves ids (so existing foreign keys keep working), derives each
user's role from their profile/superuser status, and copies group/permission
memberships.  On a fresh database (where ``auth_user`` was never created
because the user model is swapped) it is a no-op.
"""

from django.db import migrations


def table_exists(connection, name):
    with connection.cursor() as cursor:
        if connection.vendor == "postgresql":
            cursor.execute("SELECT to_regclass(%s)", (name,))
            return cursor.fetchone()[0] is not None
        cursor.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=%s",
            (name,),
        )
        return cursor.fetchone()[0] > 0


def copy_legacy_users(apps, schema_editor):
    connection = schema_editor.connection

    if not table_exists(connection, "auth_user"):
        return

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO accounts_user
                (id, password, last_login, is_superuser, username, first_name,
                 last_name, email, is_staff, is_active, date_joined, role)
            SELECT u.id, u.password, u.last_login, u.is_superuser, u.username,
                   u.first_name, u.last_name, u.email, u.is_staff, u.is_active,
                   u.date_joined,
                   CASE
                     WHEN u.is_superuser = true THEN 'admin'
                     WHEN EXISTS (
                         SELECT 1 FROM students_student_profile sp
                         WHERE sp.user_id = u.id
                     ) THEN 'student'
                     WHEN EXISTS (
                         SELECT 1 FROM faculty_faculty_profile fp
                         WHERE fp.user_id = u.id
                     ) THEN 'teacher'
                     ELSE 'student'
                   END
            FROM auth_user u
            """
        )

        for legacy_table, new_table in (
            ("auth_user_groups", "accounts_user_groups"),
            ("auth_user_user_permissions", "accounts_user_user_permissions"),
        ):
            if table_exists(connection, legacy_table):
                cursor.execute(
                    "INSERT INTO %s (id, user_id, group_id) "
                    "SELECT id, user_id, group_id FROM %s"
                    % (new_table, legacy_table)
                    if legacy_table == "auth_user_groups"
                    else "INSERT INTO %s (id, user_id, permission_id) "
                    "SELECT id, user_id, permission_id FROM %s"
                    % (new_table, legacy_table)
                )

        # Reset auto-increment sequences so new users keep getting fresh ids.
        if connection.vendor == "postgresql":
            cursor.execute(
                "SELECT setval(pg_get_serial_sequence('accounts_user','id'), "
                "(SELECT COALESCE(MAX(id),1) FROM accounts_user))"
            )
            cursor.execute(
                "SELECT setval(pg_get_serial_sequence('accounts_user_groups','id'), "
                "(SELECT COALESCE(MAX(id),1) FROM accounts_user_groups))"
            )
            cursor.execute(
                "SELECT setval(pg_get_serial_sequence('accounts_user_user_permissions','id'), "
                "(SELECT COALESCE(MAX(id),1) FROM accounts_user_user_permissions))"
            )
        else:
            try:
                cursor.execute(
                    "UPDATE sqlite_sequence SET seq = "
                    "(SELECT MAX(id) FROM accounts_user) WHERE name='accounts_user'"
                )
                cursor.execute(
                    "UPDATE sqlite_sequence SET seq = "
                    "(SELECT MAX(id) FROM accounts_user_groups) "
                    "WHERE name='accounts_user_groups'"
                )
                cursor.execute(
                    "UPDATE sqlite_sequence SET seq = "
                    "(SELECT MAX(id) FROM accounts_user_user_permissions) "
                    "WHERE name='accounts_user_user_permissions'"
                )
            except Exception:
                pass


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(copy_legacy_users, noop),
    ]
