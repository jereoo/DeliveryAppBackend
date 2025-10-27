# Generated migration to populate vehicle data

from django.db import migrations

def populate_vehicle_fields(apps, schema_editor):
    """
    Populate new vehicle fields from existing data
    """
    Vehicle = apps.get_model('delivery', 'Vehicle')
    from datetime import datetime
    
    for vehicle in Vehicle.objects.all():
        # If model field exists, try to split it into make and model
        if hasattr(vehicle, 'model') and vehicle.model:
            # For existing data, we'll try to split the model field
            parts = vehicle.model.split(' ', 1)  # Split on first space only
            vehicle.make = parts[0] if parts else 'Unknown'
            vehicle.model = parts[1] if len(parts) > 1 else ''
        else:
            vehicle.make = 'Unknown'
            vehicle.model = 'Unknown'
        
        # Set default year to current year for existing vehicles
        vehicle.year = datetime.now().year
        
        # Generate a temporary VIN for existing vehicles
        vehicle.vin = f"TEMP{vehicle.id:013d}"  # Pad to 17 chars
        
        vehicle.save()

def reverse_populate_vehicle_fields(apps, schema_editor):
    """
    Reverse the population (combine make and model back to model field)
    """
    Vehicle = apps.get_model('delivery', 'Vehicle')
    
    for vehicle in Vehicle.objects.all():
        if vehicle.make and vehicle.model:
            # Combine make and model back into the model field
            combined_model = f"{vehicle.make} {vehicle.model}".strip()
            vehicle.model = combined_model if combined_model else vehicle.make or vehicle.model or 'Unknown'
        vehicle.save()

class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0012_enhance_vehicle_model'),
    ]

    operations = [
        migrations.RunPython(populate_vehicle_fields, reverse_populate_vehicle_fields),
    ]