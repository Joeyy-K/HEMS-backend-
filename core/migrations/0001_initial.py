# Generated by Django 5.1.3 on 2024-11-17 20:27

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('thermostat', 'Thermostat'), ('camera', 'Camera'), ('light', 'Light')], max_length=20)),
                ('current_state', models.CharField(choices=[('on', 'On'), ('off', 'Off')], default='off', max_length=10)),
                ('last_reading', models.FloatField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('severity', models.CharField(choices=[('info', 'Info'), ('warning', 'Warning'), ('error', 'Error'), ('danger', 'Danger')], default='info', max_length=20)),
                ('resolved', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='core.device')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='EnergyData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('energy', models.FloatField()),
                ('type', models.CharField(choices=[('consumption', 'Consumption'), ('generation', 'Generation')], default='consumption', max_length=20)),
                ('unit', models.CharField(default='kWh', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='energy_readings', to='core.device')),
            ],
            options={
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['-timestamp'], name='core_energy_timesta_4d9780_idx')],
            },
        ),
    ]