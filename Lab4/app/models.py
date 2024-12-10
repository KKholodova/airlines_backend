from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models


class Airline(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(max_length=500, verbose_name="Описание",)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(verbose_name="Фото", blank=True, null=True)

    foundation_date = models.CharField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Авиакомпания"
        verbose_name_plural = "Авиакомпании"
        db_table = "airlines"
        ordering = ("pk",)


class Flight(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(verbose_name="Дата создания", blank=True, null=True)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Создатель", related_name='owner', null=True)
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Оператор", related_name='moderator', blank=True,  null=True)

    from_airport = models.CharField(blank=True, null=True)
    to_airport = models.CharField(blank=True, null=True)
    code = models.CharField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "Авиарейс №" + str(self.pk)

    class Meta:
        verbose_name = "Авиарейс"
        verbose_name_plural = "Авиарейсы"
        db_table = "flights"
        ordering = ('-date_formation', )


class AirlineFlight(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.DO_NOTHING, blank=True, null=True)
    flight = models.ForeignKey(Flight, on_delete=models.DO_NOTHING, blank=True, null=True)
    count = models.IntegerField(default=0)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "airline_flight"
        ordering = ('pk', )
        constraints = [
            models.UniqueConstraint(fields=['airline', 'flight'], name="airline_flight_constraint")
        ]
