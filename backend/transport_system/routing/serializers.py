from rest_framework import serializers
from .models import RoutePart


class RoutePartSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutePart
        fields = ('name', 'type', 'span_count', 'time')

    def to_representation(self, instance):
        instance = super().to_representation(instance)

        instance['time'] = float(f'{instance["time"]:.6f}')
        if instance['type'] == 'WAIT':
            instance['stop_name'] = instance.pop('name')
            instance.pop('span_count')
        if instance['type'] == 'BUS':
            instance['bus'] = instance.pop('name')
        return instance
