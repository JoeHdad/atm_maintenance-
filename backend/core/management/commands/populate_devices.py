"""
Management command to create Device records from existing ExcelUpload data
"""
from django.core.management.base import BaseCommand
from core.models import ExcelUpload, Device, TechnicianDevice


class Command(BaseCommand):
    help = 'Create Device records from existing ExcelUpload parsed_data'

    def handle(self, *args, **options):
        self.stdout.write('Starting device population...')
        
        uploads = ExcelUpload.objects.all()
        total_uploads = uploads.count()
        
        if total_uploads == 0:
            self.stdout.write(self.style.WARNING('No Excel uploads found'))
            return
        
        self.stdout.write(f'Found {total_uploads} Excel uploads')
        
        devices_created = 0
        devices_skipped = 0
        assignments_created = 0
        
        for upload in uploads:
            self.stdout.write(f'\nProcessing upload: {upload.file_name}')
            self.stdout.write(f'  Technician: {upload.technician.username}')
            self.stdout.write(f'  Rows: {len(upload.parsed_data) if upload.parsed_data else 0}')
            
            if not upload.parsed_data:
                self.stdout.write(self.style.WARNING('  No parsed data'))
                continue
            
            for index, row in enumerate(upload.parsed_data):
                # Skip header row
                if index == 0:
                    first_value = row.get('col_1', '')
                    if isinstance(first_value, str) and (
                        'interaction' in first_value.lower() or 
                        'id' in first_value.lower() or
                        'gfm' in first_value.lower()
                    ):
                        continue
                
                # Extract device data
                interaction_id = row.get('col_1', '')
                gfm_cost_center = row.get('col_2', '')
                gfm_problem_type = row.get('col_3', '')
                gfm_problem_date = row.get('col_4', '')
                city = row.get('col_5', '')
                region = row.get('col_6', '')
                
                # Skip if no interaction_id
                if not interaction_id or interaction_id == 'N/A':
                    devices_skipped += 1
                    continue
                
                # Create or get device
                device, created = Device.objects.get_or_create(
                    interaction_id=interaction_id,
                    defaults={
                        'gfm_cost_center': gfm_cost_center or '',
                        'gfm_problem_type': gfm_problem_type or '',
                        'gfm_problem_date': gfm_problem_date or '',
                        'city': city or '',
                        'region': region or '',
                        'type': upload.device_type or 'Cleaning',
                    }
                )
                
                if created:
                    devices_created += 1
                    self.stdout.write(f'  ✓ Created device: {interaction_id}')
                
                # Assign to technician
                assignment, assign_created = TechnicianDevice.objects.get_or_create(
                    technician=upload.technician,
                    device=device
                )
                
                if assign_created:
                    assignments_created += 1
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'✓ Devices created: {devices_created}'))
        self.stdout.write(self.style.WARNING(f'○ Devices skipped: {devices_skipped}'))
        self.stdout.write(self.style.SUCCESS(f'✓ Assignments created: {assignments_created}'))
        self.stdout.write('='*50)
        
        # Verify
        total_devices = Device.objects.count()
        self.stdout.write(f'\nTotal devices in database: {total_devices}')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Device population complete!'))
