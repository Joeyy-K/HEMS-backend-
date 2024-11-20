from django.contrib import admin
from .models import Device, EnergyData, Alert

admin.site.register(Device)
admin.site.register(EnergyData)
admin.site.register(Alert)