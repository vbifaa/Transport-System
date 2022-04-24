import haversine as hs

from rest_framework import serializers
from .models import Bus, Stop, StopDistance


class StopCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ('name', 'latitude', 'longitude')


class StopDistanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StopDistance
        fields = ('from_stop', 'to_stop', 'distance')

    def validate(self, attrs):
        value = super().validate(attrs)

        from_stop = value['from_stop']
        to_stop = value['to_stop']

        from_loc = (from_stop.latitude, from_stop.longitude)
        to_loc = (to_stop.latitude, to_stop.longitude)

        real_distance = round(hs.haversine(from_loc, to_loc) * 1000)
        if real_distance > value['distance']:
            raise serializers.ValidationError(
                {
                    'distance': (
                        f'Расстояние должно быть больше реального. Реальное: '
                        f'{real_distance}. Было введено: {value["distance"]}.',
                    )
                }
            )

        return value


class BusGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ('route_length', 'stop_count', 'unique_stop_count')


class BusCreateSerializer(serializers.ModelSerializer):
    stops = serializers.ListField(child=serializers.CharField())
    is_roundtrip = serializers.BooleanField()

    class Meta:
        model = Bus
        fields = ('name', 'is_roundtrip', 'stops', 'velocity')

    def validate(self, attrs):
        value = super().validate(attrs)

        stops = value['stops']
        is_round = value['is_roundtrip']

        if len(stops) < 2 or (is_round and len(stops) < 3):
            raise serializers.ValidationError(
                {'stops': 'Кол-во остановок должно быть более одной'}
            )

        if is_round and stops[-1] != stops[0]:
            raise serializers.ValidationError(
                {
                    'stops': (
                        'В кольцевом маршруте начальная и конечная '
                        'остановка должны быть равны',
                    )
                }
            )
        return value
