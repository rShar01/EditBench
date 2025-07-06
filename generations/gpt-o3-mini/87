from rest_framework import viewsets

from opticalprobeapp.serializers import MeasurementSerializer, ProbeTypeSerializer, ProbeSerializer
from opticalprobeapp.models import Measurement, Probe, ProbeType

# Create your views here.

class ProbeTypeViewSet(viewsets.ModelViewSet):
    queryset = ProbeType.objects.all()
    serializer_class = ProbeTypeSerializer

class ProbeViewSet(viewsets.ModelViewSet):
    queryset = Probe.objects.all()
    serializer_class = ProbeSerializer

class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer

# сделай фильтр для MeasurementViewSet
import django_filters

class MeasurmentFilter(django_filters.FilterSet):
    class Meta:
        model = Measurement
        fields = {
            'id': ['exact'],
            # Add more filters based on the Measurement model fields if necessary.
            # Example:
            # 'value': ['exact', 'gte', 'lte'],
            # 'timestamp': ['exact', 'gte', 'lte'],
        }
