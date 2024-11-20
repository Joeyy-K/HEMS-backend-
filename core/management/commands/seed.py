from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from core.models import Device, EnergyData, Alert

class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Starting database seeding...')

        Device.objects.all().delete()
    
        devices = [
            Device.objects.create(
                name="Living Room Thermostat",
                type="thermostat",
                current_state="off",
                location="Living Room",
                metadata={"temperature_range": "18-24"}
            ),
            Device.objects.create(
                name="Security Camera",
                type="camera",
                current_state="on",
                location="Front Door",
                metadata={"resolution": "1080p"}
            ),
            Device.objects.create(
                name="Kitchen Lights",
                type="light",
                current_state="off",
                location="Kitchen",
                metadata={"brightness_levels": "0-100"}
            )
        ]

        self.stdout.write('Created devices...')

        now = timezone.now()
        energy_data_list = []
        
        for device in devices:
            for i in range(7*24): 
                timestamp = now - timedelta(hours=i)
                energy_data_list.append(
                    EnergyData(
                        device=device,
                        timestamp=timestamp,
                        energy=random.uniform(0.5, 2.5),
                        type='consumption',
                        unit='kWh'
                    )
                )

        EnergyData.objects.bulk_create(energy_data_list)
        self.stdout.write('Created energy data...')

        Alert.objects.bulk_create([
            Alert(
                title="High Energy Usage",
                message="Thermostat energy consumption above normal",
                severity="warning",
                device=devices[0],
                timestamp=now - timedelta(hours=2)
            ),
            Alert(
                title="Device Offline",
                message="Security camera connection lost",
                severity="danger",
                device=devices[1],
                timestamp=now - timedelta(hours=1)
            ),
            Alert(
                title="Maintenance Required",
                message="Kitchen lights need attention",
                severity="info",
                device=devices[2],
                timestamp=now
            )
        ])

        self.stdout.write(self.style.SUCCESS('Successfully seeded database'))