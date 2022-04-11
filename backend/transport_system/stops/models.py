from django.core.validators import MinValueValidator
from django.db import models


class Stop(models.Model):
    name = models.CharField('Название', max_length=200, unique=True)
    latitude = models.FloatField('Широта')
    longitude = models.FloatField('Долгота')


class StopDistance(models.Model):
    from_stop = models.ForeignKey(
        Stop,
        verbose_name='Остановка отправления',
        on_delete=models.CASCADE,
        related_name='distnace_to'
    )
    to_stop = models.ForeignKey(
        Stop,
        verbose_name='Остановка прибытия',
        on_delete=models.CASCADE,
        related_name='distnace_from'
    )
    distance = models.PositiveIntegerField(
        'Расстояние',
        validators=[MinValueValidator(
            1, 'Расстояния между остановками должно быть больше нуля метров.'
        )]
    )
