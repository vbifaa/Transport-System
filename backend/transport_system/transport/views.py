from rest_framework import viewsets, status
from rest_framework.decorators import action
from transport_system.actions import get_object_or_404
from rest_framework.response import Response

from .models import Bus, BusStop, Stop, StopDistance
from .models import compute_distance
from .serializers import (
    BusCreateSerializer,
    BusGetSerializer,
    StopCreateSerializer,
    StopDistanceSerializer
)


class StopViewSet(viewsets.ModelViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopCreateSerializer

    @action(['post'], detail=False)
    def add_distance(self, request, *args, **kwargs):
        from_stop = get_object_or_404(
            Stop, name=request.POST['from_stop'], msg='Cant find from_stop',
        )
        to_stop = get_object_or_404(
            Stop, name=request.POST['to_stop'], msg='Cant find to_stop',
        )

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
        stop = get_object_or_404(
            Stop, name=request.GET['name'], msg='Cant find stop',
        )
        buses = [bus.name for bus in stop.buses.all()]
        return Response({'buses': buses}, status=status.HTTP_200_OK)


class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusGetSerializer

    def list(self, request, *args, **kwargs):
        bus = get_object_or_404(
            Bus, name=request.GET['name'], msg='Cant find bus',
        )
        serializer = BusGetSerializer(bus)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = BusCreateSerializer(
            data={
                'name': request.POST['name'],
                'stops': request.POST.getlist('stops'),
                'is_roundtrip': request.POST['is_roundtrip'],
                'velocity': request.POST['velocity'],
            },
        )
        serializer.is_valid(raise_exception=True)
        self._create_bus(serializer.data)
        return Response(status=status.HTTP_201_CREATED)

    def _create_bus(self, data):
        stops = data['stops']
        is_round = data['is_roundtrip']

        route_length = self._compute_distance(
            stops=stops, is_round=is_round,
        )
        stop_count = len(stops)
        if not is_round:
            stop_count = 2*stop_count - 1

        bus = Bus.objects.create(
            name=data['name'],
            velocity=data['velocity'],
            route_length=route_length,
            stop_count=stop_count,
            unique_stop_count=0,
        )

        unique_stop_count = 0

        for stop_name in stops:
            stop = get_object_or_404(
                Stop, name=stop_name, msg='Cant find stop',
            )
            bs, created = BusStop.objects.get_or_create(
                stop=stop, bus=bus,
            )
            if created:
                unique_stop_count += 1
        bus.unique_stop_count = unique_stop_count
        bus.save()

    def _compute_distance(self, stops, is_round):
        route_length = 0
        for i in range(len(stops)):
            if i == 0:
                continue
            route_length += compute_distance(
                from_stop_name=stops[i-1], to_stop_name=stops[i],
            )
            if not is_round:
                route_length += compute_distance(
                    from_stop_name=stops[i], to_stop_name=stops[i-1],
                )
        return route_length
