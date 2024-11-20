from django.db import models
from django.utils import timezone

class Device(models.Model):
    DEVICE_TYPES = [
        ('thermostat', 'Thermostat'),
        ('camera', 'Camera'),
        ('light', 'Light'),
    ]
    
    STATE_CHOICES = [
        ('on', 'On'),
        ('off', 'Off'),
    ]
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    current_state = models.CharField(
        max_length=10, 
        choices=STATE_CHOICES,
        default='off'
    )
    last_reading = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.type})"

class EnergyData(models.Model):
    ENERGY_TYPES = [
        ('consumption', 'Consumption'),
        ('generation', 'Generation'),
    ]
    
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='energy_readings'
    )
    timestamp = models.DateTimeField(default=timezone.now)
    energy = models.FloatField()
    type = models.CharField(
        max_length=20,
        choices=ENERGY_TYPES,
        default='consumption'
    )
    unit = models.CharField(max_length=10, default='kWh')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"{self.device.name} - {self.energy}{self.unit} at {self.timestamp}"

class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('danger', 'Danger'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='info'
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='alerts',
        null=True,
        blank=True
    )
    resolved = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.severity}: {self.title}"