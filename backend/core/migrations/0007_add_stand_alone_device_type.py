# Generated migration for adding 'Stand Alone' device type

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_fix_submission_unique_constraint'),
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
                    ('Stand Alone', 'Stand Alone'),
                ],
                help_text='Maintenance type',
                max_length=20
            ),
        ),
    ]
