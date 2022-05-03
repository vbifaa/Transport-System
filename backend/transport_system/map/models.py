from django.db import models


class MapStop(models.Model):
    name = models.CharField('Название', max_length=25, unique=True)
    x_map_id = models.PositiveIntegerField()
    y_map_id = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['x_map_id', 'y_map_id'], name='unique_coordinate',
            )
        ]


class MapBus(models.Model):

    class BusType(models.TextChoices):
        ROUND = 'ROUND'
        BACKWARD = 'BACKWARD'

    name = models.CharField('Название', max_length=25, unique=True)
    stops = models.JSONField()
    type = models.CharField(choices=BusType.choices, max_length=200)
