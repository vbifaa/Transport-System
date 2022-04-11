from rest_framework import serializers
from .models import Stop


class StopCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = (
            'name', 'latitude', 'longitude',
        )
