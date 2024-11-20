from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Avg
from django_filters import rest_framework as django_filters
from datetime import timedelta

from .models import Device, EnergyData, Alert
from .serializers import (
    DeviceSerializer, 
    DeviceDetailSerializer,
    DeviceStateUpdateSerializer,
    DeviceStatisticsSerializer,
    EnergyDataSerializer,
    EnergyDataFilterSerializer,
    AlertSerializer
)

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    filter_backends = [filters.SearchFilter, django_filters.DjangoFilterBackend]
    search_fields = ['name', 'location']
    filterset_fields = ['type', 'current_state']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DeviceDetailSerializer
        return DeviceSerializer

    @action(detail=True, methods=['post'])
    def control(self, request, pk=None):
        device = self.get_object()
        serializer = DeviceStateUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            reason = serializer.validated_data.get('reason', '')

            device.current_state = action
            device.save()
            
            if reason:
                Alert.objects.create(
                    title=f"Device State Changed: {device.name}",
                    message=f"State changed to {action}. Reason: {reason}",
                    severity='info',
                    device=device
                )
            
            return Response({
                'status': 'success',
                'current_state': device.current_state
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True)
    def statistics(self, request, pk=None):
        device = self.get_object()
        last_24h = timezone.now() - timedelta(hours=24)
        
        stats = {
            'total_energy': EnergyData.objects.filter(
                device=device,
                timestamp__gte=last_24h
            ).aggregate(total=Sum('energy'))['total'] or 0,
            
            'average_energy': EnergyData.objects.filter(
                device=device,
                timestamp__gte=last_24h
            ).aggregate(avg=Avg('energy'))['avg'] or 0,
            
            'alert_count': Alert.objects.filter(
                device=device,
                resolved=False
            ).count(),
            
            'last_reading_timestamp': EnergyData.objects.filter(
                device=device
            ).order_by('-timestamp').first().timestamp if EnergyData.objects.filter(
                device=device
            ).exists() else None
        }
        
        serializer = DeviceStatisticsSerializer(stats)
        return Response(serializer.data)

class EnergyDataViewSet(viewsets.ModelViewSet):
    queryset = EnergyData.objects.all()
    serializer_class = EnergyDataSerializer
    filterset_fields = ['device', 'type']

    def get_queryset(self):
        queryset = EnergyData.objects.all()
        
        filter_serializer = EnergyDataFilterSerializer(data=self.request.query_params)
        if filter_serializer.is_valid():
            if filter_serializer.validated_data.get('start_date'):
                queryset = queryset.filter(
                    timestamp__gte=filter_serializer.validated_data['start_date'],
                    timestamp__lte=filter_serializer.validated_data['end_date']
                )
            
            if filter_serializer.validated_data.get('device_id'):
                queryset = queryset.filter(
                    device_id=filter_serializer.validated_data['device_id']
                )
                
            if filter_serializer.validated_data.get('type'):
                queryset = queryset.filter(
                    type=filter_serializer.validated_data['type']
                )
        
        return queryset.select_related('device')

    @action(detail=False)
    def summary(self, request):
        today = timezone.now().date()
        
        daily_consumption = EnergyData.objects.filter(
            timestamp__date=today,
            type='consumption'
        ).aggregate(
            total=Sum('energy'),
            average=Avg('energy')
        )
        
        return Response({
            'date': today,
            'total_consumption': daily_consumption['total'] or 0,
            'average_consumption': daily_consumption['average'] or 0
        })

class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    filterset_fields = ['severity', 'resolved', 'device']

    def get_queryset(self):
        return Alert.objects.all().select_related('device')

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.resolved = True
        alert.save()
        return Response({
            'status': 'success',
            'message': 'Alert resolved successfully'
        })

    @action(detail=False)
    def unresolved(self, request):
        unresolved = Alert.objects.filter(resolved=False)
        serializer = self.get_serializer(unresolved, many=True)
        return Response(serializer.data)

class EnergyDataFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    min_energy = django_filters.NumberFilter(field_name='energy', lookup_expr='gte')
    max_energy = django_filters.NumberFilter(field_name='energy', lookup_expr='lte')

    class Meta:
        model = EnergyData
        fields = ['device', 'type', 'unit']
