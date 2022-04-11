from rest_framework import viewsets
from .models import Stop
from .serializers import StopCreateSerializer


class StopViewSet(viewsets.ModelViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopCreateSerializer
