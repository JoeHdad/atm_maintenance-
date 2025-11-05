# Generated migration for updating device type choices

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_submission_job_status_alter_submission_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='type',
            field=models.CharField(
                choices=[
                    ('Cleaning1', 'Cleaning1'),
                    ('Cleaning2', 'Cleaning2'),
                    ('Electrical', 'Electrical'),
                    ('Security', 'Security'),
                ],
                help_text='Maintenance type',
                max_length=20
            ),
        ),
    ]
