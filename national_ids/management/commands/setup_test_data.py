from django.core.management.base import BaseCommand
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = 'Set up test data for the Egyptian ID API'

    def handle(self, *args, **options):
        self.stdout.write('Setting up test data...')
        
        # Run migrations first
        self.stdout.write('Running migrations...')
        call_command('migrate', verbosity=0)
        
        # Load fixtures
        self.stdout.write('Loading test fixtures...')
        fixtures_path = os.path.join('fixtures', 'test_data.json')
        call_command('loaddata', fixtures_path, verbosity=0)
        
        self.stdout.write(
            self.style.SUCCESS('\nTest data setup complete!\n')
        )
        
        self.stdout.write('Available test accounts:')
        self.stdout.write('• Admin: admin@test.com / admin123 (1000 tokens)')
        self.stdout.write('• Tester: tester@test.com / test123 (500 tokens)')
        self.stdout.write('• Demo: demo@test.com / demo123 (100 tokens)')
        
        self.stdout.write('\nAPI Keys for testing:')
        self.stdout.write('• Admin: nid_admin_test_key_123456789012345678901234')
        self.stdout.write('• Test: nid_test_key_123456789012345678901234567')
        self.stdout.write('• Demo: nid_demo_key_123456789012345678901234567')
        
        self.stdout.write('\nTest the API with:')
        self.stdout.write('curl -X POST http://localhost:8000/api/v1/national-ids/egyptian-id/extract/ \\')
        self.stdout.write('     -H "X-API-Key: nid_test_key_123456789012345678901234567" \\')
        self.stdout.write('     -H "Content-Type: application/json" \\')
        self.stdout.write('     -d \'{"national_id": "29001010123456"}\'') 