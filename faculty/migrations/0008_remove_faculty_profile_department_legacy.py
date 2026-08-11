from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("faculty", "0007_link_faculty_departments"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="faculty_profile",
            name="department_legacy",
        ),
    ]
