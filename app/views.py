from django.shortcuts import render

airlines = [
    {
        "id": 1,
        "name": "Аэрофлот",
        "description": "«Аэрофлот — российские авиалинии» — российская государственно-частная авиакомпания, образованная из одного из государственных социалистических предприятий, входившего в состав советского «Аэрофлота» и осуществлявшего полёты и коммерческую деятельность на международных воздушных линиях, а также завладевшего правами на одноимённую торговую марку.",
        "image": "http://localhost:9000/images/1.png",
        "foundation_date": "17 марта 1923г"
    },
    {
        "id": 2,
        "name": "Победа",
        "description": "«Побе́да» (юридическое название — ООО «Авиакомпания Победа») — российская бюджетная авиакомпания, дочернее предприятие группы «Аэрофлот — Российские авиалинии», базируется в московском аэропорту Внуково. Основана 16 сентября 2014 года взамен прекратившего полёты из-за санкций Европейского союза «Добролёта». Суточный налёт самолётов авиакомпании в 2017 году был самым высоким в мире — 15—16 часов, что было выше, чем у крупнейших мировых лоукостеров — американской Southwest и ирландской Ryanair.",
        "image": "http://localhost:9000/images/2.png",
        "foundation_date": "16 сентября 2014г"
    },
    {
        "id": 3,
        "name": "Россия",
        "description": "Росси́я (юридическое название АО «Авиакомпания «Россия») — российская авиакомпания, входит в состав группы «Аэрофлот». Один из крупнейших авиаперевозчиков России. Основана 7 мая 1934 года. Специализируется на перевозках в среднем ценовом сегменте и предоставляет пассажирам полный спектр сервиса в двух классах обслуживания — экономический и бизнес.",
        "image": "http://localhost:9000/images/3.png",
        "foundation_date": "1934г"
    },
    {
        "id": 4,
        "name": "Уральские авиалинии",
        "description": "Ура́льские авиали́нии — российская пассажирская авиакомпания, занимающаяся регулярными и чартерными внутренними и международными перевозками. Штаб-квартира расположена в Екатеринбурге. Парк воздушных судов авиакомпании «Уральские Авиалинии» состоит из самолётов семейства А320 концерна Airbus, что очень упрощает обучению пилотов. У компании есть хабы в екатеринбургском аэропорту «Кольцово» и московском аэропорту «Домодедово», а также центры технического обслуживания судов в аэропортах «Кольцово» (Екатеринбург), «Домодедово» (Москва), «Пулково» (Санкт-Петербург).",
        "image": "http://localhost:9000/images/4.png",
        "foundation_date": "1943г"
    },
    {
        "id": 5,
        "name": "S7 Airlines",
        "description": "S7 Airlines (рус. эс сэвэн эйрлайнс, юридическое наименование: акционерное общество «Авиакомпания „Сибирь“») — российская авиакомпания, выполняет внутренние и международные пассажирские авиаперевозки, входит в перечень системообразующих организаций России, является крупнейшей частной авиакомпанией России. До апреля 2022 года являлась членом глобального авиационного альянса Oneworld, по состоянию на октябрь 2022 года членство приостановлено.",
        "image": "http://localhost:9000/images/5.png",
        "foundation_date": "6 мая 1992г"
    },
    {
        "id": 6,
        "name": "Ред Вингс",
        "description": "S7 Airlines (рус. эс сэвэн эйрлайнс, юридическое наименование: акционерное общество «Авиакомпания „Сибирь“») — российская авиакомпания, выполняет внутренние и международные пассажирские авиаперевозки, входит в перечень системообразующих организаций России, является крупнейшей частной авиакомпанией России. До апреля 2022 года являлась членом глобального авиационного альянса Oneworld, по состоянию на октябрь 2022 года членство приостановлено.",
        "image": "http://localhost:9000/images/5.png",
        "foundation_date": "1999г"
    }
]

draft_flight = {
    "id": 123,
    "status": "Черновик",
    "date_created": "12 сентября 2024г",
    "from": "Домодедово",
    "to": "Архангельск",
    "date": "5 октября 2024г 12:00",
    "code": "RUS-1727",
    "airlines": [
        {
            "id": 1,
            "count": 100
        },
        {
            "id": 2,
            "count": 125
        },
        {
            "id": 3,
            "count": 75
        }
    ]
}


def getAirlineById(airline_id):
    for airline in airlines:
        if airline["id"] == airline_id:
            return airline


def getAirlines():
    return airlines


def searchAirlines(airline_name):
    res = []

    for airline in airlines:
        if airline_name.lower() in airline["name"].lower():
            res.append(airline)

    return res


def getDraftFlight():
    return draft_flight


def getFlightById(flight_id):
    return draft_flight


def index(request):
    airline_name = request.GET.get("airline_name", "")
    airlines = searchAirlines(airline_name) if airline_name else getAirlines()
    draft_flight = getDraftFlight()

    context = {
        "airlines": airlines,
        "airline_name": airline_name,
        "airlines_count": len(draft_flight["airlines"]),
        "draft_flight": draft_flight
    }

    return render(request, "home_page.html", context)


def airline(request, airline_id):
    context = {
        "id": airline_id,
        "airline": getAirlineById(airline_id),
    }

    return render(request, "airline_page.html", context)


def flight(request, flight_id):
    flight = getFlightById(flight_id)
    airlines = [
        {**getAirlineById(airline["id"]), "count": airline["count"]}
        for airline in flight["airlines"]
    ]

    context = {
        "flight": flight,
        "airlines": airlines
    }

    return render(request, "flight_page.html", context)
