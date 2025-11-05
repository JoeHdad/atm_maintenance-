# Migration to replace legacy unique_together with conditional UniqueConstraint
# This allows rejected submissions to be resubmitted without violating uniqueness

from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_add_stand_alone_device_type'),
    ]

    operations = [
        # Remove the old unconditional unique_together constraint
        migrations.AlterUniqueTogether(
            name='submission',
            unique_together=set(),
        ),

        # Add the new conditional UniqueConstraint that excludes rejected submissions
        migrations.AddConstraint(
            model_name='submission',
            constraint=models.UniqueConstraint(
                fields=['technician', 'device', 'half_month'],
                condition=~Q(status='Rejected'),
                name='unique_submission_per_half_month_active'
            ),
        ),
    ]
