from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0007_link_student_departments"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="student_profile",
            name="department_legacy",
        ),
    ]
