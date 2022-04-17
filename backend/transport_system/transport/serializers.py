import haversine as hs

from rest_framework import serializers
from .models import Stop, StopDistance


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
