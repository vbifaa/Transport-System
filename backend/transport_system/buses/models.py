from django.core.validators import MinValueValidator
from django.db import models

from stops.models import Stop


class Bus(models.Model):
    name = models.CharField('Название', max_length=25, unique=True)
    route_length = models.PositiveIntegerField(
        'Расстояние',
        validators=[MinValueValidator(
            1, 'Расстояния между остановками должно быть более нуля метров.'
        )]
    )
    stop_count = models.PositiveIntegerField(
        'Кол-во остановок',
        validators=[MinValueValidator(
            1, 'Кол-во остановок должно быть больше нуля.'
        )]
    )
    unique_stop_count = models.PositiveIntegerField(
        'Кол-во уникальных остановок',
        validators=[MinValueValidator(
            1, 'Кол-во уникальных остановок должно быть больше нуля.'
        )]
    )


class BusStop(models.Model):
    stop = models.ForeignKey(
        Stop,
        verbose_name='Остановка через которую едет автобус',
        on_delete=models.CASCADE,
        related_name='buses'
    )
    bus = models.ForeignKey(
        Bus,
        verbose_name='Автобус который едет через остановку',
        on_delete=models.CASCADE,
        related_name='stops'
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['stop', 'bus'], name='unique_bus_stop'
            )
        ]
