from django.core.validators import MinValueValidator
from django.db import models


class Stop(models.Model):
    name = models.CharField('Название', max_length=50, unique=True)
    longitude = models.FloatField('Долгота')
    latitude = models.FloatField('Широта')

    in_id = models.PositiveIntegerField(
        'Id вершины входа в остановку', null=True, unique=True,
    )
    out_id = models.PositiveIntegerField(
        'Id вершины выхода из остановки', null=True, unique=True,
    )


class StopDistance(models.Model):
    from_stop = models.ForeignKey(
        Stop,
        verbose_name='Остановка отправления',
        on_delete=models.CASCADE,
        related_name='distnace_to',
    )
    to_stop = models.ForeignKey(
        Stop,
        verbose_name='Остановка прибытия',
        on_delete=models.CASCADE,
        related_name='distnace_from',
    )
    distance = models.PositiveIntegerField(
        'Расстояние',
        validators=[MinValueValidator(
            1, 'Расстояния между остановками должно быть более нуля метров.',
        )]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['from_stop', 'to_stop'], name='unique_distance',
            )
        ]


def compute_distance(from_stop_name, to_stop_name):
    dist = StopDistance.objects.filter(
        from_stop__name=from_stop_name, to_stop__name=to_stop_name,
    ).first()
    if dist is None:
        dist = StopDistance.objects.filter(
            from_stop__name=to_stop_name, to_stop__name=from_stop_name,
        ).first()
    if dist is None:
        from rest_framework.exceptions import NotFound
        raise NotFound(
            f'No distance between {from_stop_name} and {to_stop_name}',
        )
    return dist.distance


class Bus(models.Model):
    name = models.CharField('Название', max_length=25, unique=True)
    velocity = models.PositiveIntegerField(
        'Скорость автобуса в км/ч',
        validators=[MinValueValidator(
            1, 'Скорость должна быть положительной.',
        )]
    )
    route_length = models.PositiveIntegerField(
        'Расстояние',
        validators=[MinValueValidator(
            1, 'Расстояния между остановками должно быть более нуля метров.',
        )]
    )
    stop_count = models.PositiveIntegerField(
        'Кол-во остановок',
        validators=[MinValueValidator(
            1, 'Кол-во остановок должно быть больше нуля.',
        )]
    )
    unique_stop_count = models.PositiveIntegerField(
        'Кол-во уникальных остановок',
        validators=[MinValueValidator(
            1, 'Кол-во уникальных остановок должно быть больше нуля.',
        )]
    )
    stops = models.ManyToManyField(
        Stop,
        verbose_name='Остановка',
        related_name='buses',
        through='BusStop',
    )


class BusStop(models.Model):
    stop = models.ForeignKey(
        Stop,
        verbose_name='Остановка через которую едет автобус',
        on_delete=models.CASCADE,
    )
    bus = models.ForeignKey(
        Bus,
        verbose_name='Автобус который едет через остановку',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['stop', 'bus'], name='unique_bus_stop',
            )
        ]
