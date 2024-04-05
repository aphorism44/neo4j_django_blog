# myapp/management/commands/import_csv_data.py

from django.core.management.base import BaseCommand
from myapp.utils import import_csv_to_neo4j

class Command(BaseCommand):
    help = 'Import data from CSV file to Neo4j'

    def handle(self, *args, **options):
        file_path = '../../import_neo4j_data.csv'  # Replace with the actual path to your CSV file
        import_csv_to_neo4j(file_path)
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
