from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import Airline, Flight, AirlineFlight


def index(request):
    airline_name = request.GET.get("airline_name", "")
    airlines = Airline.objects.filter(status=1)

    if airline_name:
        airlines = airlines.filter(name__icontains=airline_name)

    draft_flight = get_draft_flight()

    context = {
        "airline_name": airline_name,
        "airlines": airlines
    }

    if draft_flight:
        context["airlines_count"] = len(draft_flight.get_airlines())
        context["draft_flight"] = draft_flight

    return render(request, "home_page.html", context)


def add_airline_to_draft_flight(request, airline_id):
    airline = Airline.objects.get(pk=airline_id)

    draft_flight = get_draft_flight()

    if draft_flight is None:
        draft_flight = Flight.objects.create()
        draft_flight.owner = get_current_user()
        draft_flight.date_created = timezone.now()
        draft_flight.save()

    if AirlineFlight.objects.filter(flight=draft_flight, airline=airline).exists():
        return redirect("/")

    item = AirlineFlight(
        flight=draft_flight,
        airline=airline
    )
    item.save()

    return redirect("/")


def airline_details(request, airline_id):
    context = {
        "airline": Airline.objects.get(id=airline_id)
    }

    return render(request, "airline_page.html", context)


def delete_flight(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM airline_flight WHERE flight_id = %s", [flight_id])
        cursor.execute("DELETE FROM flights WHERE id = %s", [flight_id])

    return redirect("/")


def flight(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return redirect("/")

    context = {
        "flight": Flight.objects.get(id=flight_id),
    }

    return render(request, "flight_page.html", context)


def get_draft_flight():
    return Flight.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()