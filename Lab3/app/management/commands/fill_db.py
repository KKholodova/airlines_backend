import random

from django.core.management.base import BaseCommand
from minio import Minio

from ...models import *
from .utils import random_date, random_timedelta


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")

    print("Пользователи созданы")


def add_airlines():
    Airline.objects.create(
        name="Аэрофлот",
        description="«Аэрофлот — российские авиалинии» — российская государственно-частная авиакомпания, образованная из одного из государственных социалистических предприятий, входившего в состав советского «Аэрофлота» и осуществлявшего полёты и коммерческую деятельность на международных воздушных линиях, а также завладевшего правами на одноимённую торговую марку.",
        foundation_date="17 марта 1923г",
        image="1.png"
    )

    Airline.objects.create(
        name="Победа",
        description="«Побе́да» (юридическое название — ООО «Авиакомпания Победа») — российская бюджетная авиакомпания, дочернее предприятие группы «Аэрофлот — Российские авиалинии», базируется в московском аэропорту Внуково. Основана 16 сентября 2014 года взамен прекратившего полёты из-за санкций Европейского союза «Добролёта». Суточный налёт самолётов авиакомпании в 2017 году был самым высоким в мире — 15—16 часов, что было выше, чем у крупнейших мировых лоукостеров — американской Southwest и ирландской Ryanair.",
        foundation_date="16 сентября 2014г",
        image="2.png"
    )

    Airline.objects.create(
        name="Россия",
        description="Росси́я (юридическое название АО «Авиакомпания «Россия») — российская авиакомпания, входит в состав группы «Аэрофлот». Один из крупнейших авиаперевозчиков России. Основана 7 мая 1934 года. Специализируется на перевозках в среднем ценовом сегменте и предоставляет пассажирам полный спектр сервиса в двух классах обслуживания — экономический и бизнес.",
        foundation_date="1934г",
        image="3.png"
    )

    Airline.objects.create(
        name="Уральские авиалинии",
        description="Ура́льские авиали́нии — российская пассажирская авиакомпания, занимающаяся регулярными и чартерными внутренними и международными перевозками. Штаб-квартира расположена в Екатеринбурге. Парк воздушных судов авиакомпании «Уральские Авиалинии» состоит из самолётов семейства А320 концерна Airbus, что очень упрощает обучению пилотов. У компании есть хабы в екатеринбургском аэропорту «Кольцово» и московском аэропорту «Домодедово», а также центры технического обслуживания судов в аэропортах «Кольцово» (Екатеринбург), «Домодедово» (Москва), «Пулково» (Санкт-Петербург).",
        foundation_date="1943г",
        image="4.png"
    )

    Airline.objects.create(
        name="S7 Airlines",
        description="S7 Airlines — российская авиакомпания, выполняет внутренние и международные пассажирские авиаперевозки, входит в перечень системообразующих организаций России, является крупнейшей частной авиакомпанией России. До апреля 2022 года являлась членом глобального авиационного альянса Oneworld, по состоянию на октябрь 2022 года членство приостановлено.",
        foundation_date="6 мая 1992г",
        image="5.png"
    )

    Airline.objects.create(
        name="Ред Вингс",
        description="S7 Airlines (рус. эс сэвэн эйрлайнс, юридическое наименование: акционерное общество «Авиакомпания „Сибирь“») — российская авиакомпания, выполняет внутренние и международные пассажирские авиаперевозки, входит в перечень системообразующих организаций России, является крупнейшей частной авиакомпанией России. До апреля 2022 года являлась членом глобального авиационного альянса Oneworld, по состоянию на октябрь 2022 года членство приостановлено.",
        foundation_date="1999г",
        image="6.png"
    )

    client = Minio("minio:9000", "minio", "minio123", secure=False)
    client.fput_object('images', '1.png', "app/static/images/1.png")
    client.fput_object('images', '2.png', "app/static/images/2.png")
    client.fput_object('images', '3.png', "app/static/images/3.png")
    client.fput_object('images', '4.png', "app/static/images/4.png")
    client.fput_object('images', '5.png', "app/static/images/5.png")
    client.fput_object('images', '6.png', "app/static/images/6.png")
    client.fput_object('images', 'default.png', "app/static/images/default.png")

    print("Услуги добавлены")


def add_flights():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)

    if len(users) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    airlines = Airline.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_flight(status, airlines, owner, moderators)

    add_flight(1, airlines, users[0], moderators)
    add_flight(2, airlines, users[0], moderators)

    print("Заявки добавлены")


def add_flight(status, airlines, owner, moderators):
    flight = Flight.objects.create()
    flight.status = status

    if flight.status in [3, 4]:
        flight.date_complete = random_date()
        flight.date_formation = flight.date_complete - random_timedelta()
        flight.date_created = flight.date_formation - random_timedelta()
    else:
        flight.date_formation = random_date()
        flight.date_created = flight.date_formation - random_timedelta()

    flight.owner = owner
    flight.moderator = random.choice(moderators)
    
    flight.from_airport = "Домодево"
    flight.to_airport = "Архангельск"
    flight.date = random_date()
    flight.code = "RUS-1727"

    for airline in random.sample(list(airlines), 3):
        item = AirlineFlight(
            flight=flight,
            airline=airline,
            value=random.randint(1, 10)
        )
        item.save()

    flight.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_airlines()
        add_flights()
