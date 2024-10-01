from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User

from app.utils import STATUS_CHOICES


class Airline(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(default="images/default.png")
    description = models.TextField(verbose_name="Описание", blank=True)
    foundation_date = models.CharField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Авиакомпания"
        verbose_name_plural = "Авиакомпании"
        db_table = "airlines"


class Flight(models.Model):
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=timezone.now(), verbose_name="Дата создания")
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", null=True, related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Модератор", null=True, related_name='moderator')

    from_airport = models.CharField(default="Домодедово", blank=True, null=True)
    to_airport = models.CharField(default="Астрахань", blank=True, null=True)
    date = models.DateTimeField(default=timezone.now(), blank=True, null=True)
    code = models.CharField(default="RUS-1727", blank=True, null=True)

    def __str__(self):
        return "Авиарейс №" + str(self.pk)

    def get_airlines(self):
        return [
            setattr(item.airline, "value", item.value) or item.airline
            for item in AirlineFlight.objects.filter(flight=self)
        ]

    def get_status(self):
        return dict(STATUS_CHOICES).get(self.status)

    class Meta:
        verbose_name = "Авиарейс"
        verbose_name_plural = "Авиарейсы"
        ordering = ('-date_formation', )
        db_table = "flights"


class AirlineFlight(models.Model):
    airline = models.ForeignKey(Airline, models.DO_NOTHING, blank=True, null=True)
    flight = models.ForeignKey(Flight, models.DO_NOTHING, blank=True, null=True)
    value = models.IntegerField(verbose_name="Поле м-м", blank=True, null=True)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "airline_flight"
