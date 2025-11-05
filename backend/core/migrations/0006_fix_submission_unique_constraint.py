# Generated migration for fixing submission unique constraint to include technician

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_device_type_choices'),
    ]

    operations = [
        # First, remove the old unique constraint
        migrations.AlterUniqueTogether(
            name='submission',
            unique_together=set(),
        ),

        # Add the new unique constraint that includes technician
        migrations.AlterUniqueTogether(
            name='submission',
            unique_together={('technician', 'device', 'half_month')},
        ),

        # Add index for technician + device queries
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['technician', 'device'], name='submission_technician_device_idx'),
        ),
    ]
