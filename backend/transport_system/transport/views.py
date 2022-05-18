from copy import deepcopy

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from map.models import MapBus
from map.views import settings as draw_settings
from routing.models import router_wrapper as rw
from transport_system.actions import get_object_or_404

from .models import Bus, BusStop, Stop, StopDistance, compute_distance
from .serializers import (BusCreateSerializer, BusGetSerializer,
                          StopCreateSerializer, StopDistanceSerializer)


class StopViewSet(viewsets.ModelViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopCreateSerializer

    def create(self, request, *args, **kwargs):
        obj = super().create(request, *args, **kwargs)
        rw.add_stop(obj.data['name'])
        return obj

    @action(['post'], detail=False)
    def add_distance(self, request, *args, **kwargs):
        from_stop = get_object_or_404(
            Stop, name=request.data['from_stop'], msg='Cant find from_stop',
        )
        to_stop = get_object_or_404(
            Stop, name=request.data['to_stop'], msg='Cant find to_stop',
        )

        serializer = StopDistanceSerializer(
            data={
                'from_stop': from_stop.pk,
                'to_stop': to_stop.pk,
                'distance': request.data['distance'],
            },
        )
        serializer.is_valid(raise_exception=True)

        StopDistance.objects.create(
            from_stop=from_stop,
            to_stop=to_stop,
            distance=request.data['distance'],
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
        serializer = BusCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self._create_bus(deepcopy(serializer.data))
        self._create_map_bus(deepcopy(serializer.data))
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
            _, created = BusStop.objects.get_or_create(
                stop=stop, bus=bus,
            )
            if created:
                unique_stop_count += 1
        bus.unique_stop_count = unique_stop_count
        bus.save()

        rw.add_bus(bus_name=data['name'], stops=stops, one_direction=is_round)

    def _create_map_bus(self, data):
        draw_settings.map_build = False
        data.pop('velocity')
        data['type'] = 'ROUND' if data.pop('is_roundtrip') else 'BACKWARD'
        MapBus.objects.create(**data)

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
