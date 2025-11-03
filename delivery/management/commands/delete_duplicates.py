from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from delivery.models import Customer, Driver, Vehicle
from collections import defaultdict

class Command(BaseCommand):
    help = 'Delete duplicate users, customers, drivers, and vehicles (keeps the first record for each unique field)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Deleting duplicate Users by username and email...'))
        self.delete_duplicates(User, ['username'])
        self.delete_duplicates(User, ['email'])

        self.stdout.write(self.style.WARNING('Deleting duplicate Customers by user_id...'))
        self.delete_duplicates(Customer, ['user_id'])

        self.stdout.write(self.style.WARNING('Deleting duplicate Drivers by license_number...'))
        self.delete_duplicates(Driver, ['license_number'])

        self.stdout.write(self.style.WARNING('Deleting duplicate Vehicles by license_plate...'))
        self.delete_duplicates(Vehicle, ['license_plate'])

        self.stdout.write(self.style.SUCCESS('Duplicate cleanup complete.'))

    def delete_duplicates(self, model, unique_fields):
        seen = set()
        duplicates = []
        for obj in model.objects.all().order_by('id'):
            key = tuple(getattr(obj, field) for field in unique_fields)
            if key in seen:
                duplicates.append(obj)
            else:
                seen.add(key)
        count = len(duplicates)
        if count:
            for obj in duplicates:
                obj.delete()
            self.stdout.write(self.style.NOTICE(f'Deleted {count} duplicates from {model.__name__}'))
        else:
            self.stdout.write(f'No duplicates found for {model.__name__}')
