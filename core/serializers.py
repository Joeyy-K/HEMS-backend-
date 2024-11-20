from rest_framework import serializers
from .models import Device, EnergyData, Alert

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            'id', 
            'name', 
            'type', 
            'current_state', 
            'last_reading',
            'location',
            'metadata',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_metadata(self, value):
        """
        Ensure metadata is a valid JSON object
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Metadata must be a JSON object")
        return value

class EnergyDataSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = EnergyData
        fields = [
            'id',
            'device',
            'device_name',
            'timestamp',
            'energy',
            'type',
            'unit',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_energy(self, value):
        """
        Validate energy reading is positive
        """
        if value < 0:
            raise serializers.ValidationError("Energy reading cannot be negative")
        return value

class AlertSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id',
            'title',
            'message',
            'severity',
            'device',
            'device_name',
            'resolved',
            'timestamp',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class DeviceDetailSerializer(DeviceSerializer):
    energy_readings = EnergyDataSerializer(many=True, read_only=True)
    alerts = AlertSerializer(many=True, read_only=True)
    
    class Meta(DeviceSerializer.Meta):
        fields = DeviceSerializer.Meta.fields + ['energy_readings', 'alerts']

class DeviceStatisticsSerializer(serializers.Serializer):
    total_energy = serializers.FloatField()
    average_energy = serializers.FloatField()
    alert_count = serializers.IntegerField()
    last_reading_timestamp = serializers.DateTimeField()
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['total_energy'] = round(data['total_energy'], 2)
        data['average_energy'] = round(data['average_energy'], 2)
        return data

class DeviceStateUpdateSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['on', 'off'])
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate_action(self, value):
        """
        Validate the action is a valid state transition
        """
        return value

class EnergyDataFilterSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    device_id = serializers.IntegerField(required=False)
    type = serializers.ChoiceField(
        choices=['consumption', 'generation'],
        required=False
    )

    def validate(self, data):
        """
        Validate that if one date is provided, both are provided
        """
        if ('start_date' in data and 'end_date' not in data) or \
           ('end_date' in data and 'start_date' not in data):
            raise serializers.ValidationError(
                "Both start_date and end_date must be provided together"
            )
        
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError(
                    "End date must be after start date"
                )
        
        return data