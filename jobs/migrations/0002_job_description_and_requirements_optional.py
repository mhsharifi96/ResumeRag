from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobposition",
            name="job_description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="jobposition",
            name="requirements",
            field=models.TextField(blank=True, default=""),
        ),
    ]
