from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Stop, StopDistance
from .serializers import StopCreateSerializer, StopDistanceSerializer


class StopViewSet(viewsets.ModelViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopCreateSerializer

    @action(['post'], detail=False)
    def add_distance(self, request, *args, **kwargs):
        from_stop = get_object_or_404(Stop, name=request.POST['from_stop'])
        to_stop = get_object_or_404(Stop, name=request.POST['to_stop'])

        serializer = StopDistanceSerializer(
            data={
                'from_stop': from_stop.pk,
                'to_stop': to_stop.pk,
                'distance': request.POST['distance'],
            },
        )
        serializer.is_valid(raise_exception=True)

        StopDistance.objects.create(
            from_stop=from_stop,
            to_stop=to_stop,
            distance=request.POST['distance'],
        )
        return Response(status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        stop = get_object_or_404(Stop, name=request.GET['name'])
        buses = [bus.bus.name for bus in stop.buses.all()]
        return Response({'buses': buses}, status=status.HTTP_200_OK)
