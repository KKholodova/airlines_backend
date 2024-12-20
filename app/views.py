import random
from datetime import datetime, timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *


def get_draft_flight():
    return Flight.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


@api_view(["GET"])
def search_airlines(request):
    airline_name = request.GET.get("airline_name", "")

    airlines = Airline.objects.filter(status=1)

    if airline_name:
        airlines = airlines.filter(name__icontains=airline_name)

    serializer = AirlinesSerializer(airlines, many=True)
    
    draft_flight = get_draft_flight()

    resp = {
        "airlines": serializer.data,
        "airlines_count": AirlineFlight.objects.filter(flight=draft_flight).count() if draft_flight else None,
        "draft_flight": draft_flight.pk if draft_flight else None
    }

    return Response(resp)


@api_view(["GET"])
def get_airline_by_id(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)
    serializer = AirlineSerializer(airline)

    return Response(serializer.data)


@api_view(["PUT"])
def update_airline(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)

    serializer = AirlineSerializer(airline, data=request.data, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_airline(request):
    serializer = AirlineSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Airline.objects.create(**serializer.validated_data)

    airlines = Airline.objects.filter(status=1)
    serializer = AirlineSerializer(airlines, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_airline(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)
    airline.status = 2
    airline.save()

    airlines = Airline.objects.filter(status=1)
    serializer = AirlineSerializer(airlines, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_airline_to_flight(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)

    draft_flight = get_draft_flight()

    if draft_flight is None:
        draft_flight = Flight.objects.create()
        draft_flight.owner = get_user()
        draft_flight.date_created = timezone.now()
        draft_flight.save()

    if AirlineFlight.objects.filter(flight=draft_flight, airline=airline).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    item = AirlineFlight.objects.create()
    item.flight = draft_flight
    item.airline = airline
    item.save()

    serializer = FlightSerializer(draft_flight)
    return Response(serializer.data["airlines"])


@api_view(["POST"])
def update_airline_image(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)

    image = request.data.get("image")
    if image is not None:
        airline.image = image
        airline.save()

    serializer = AirlineSerializer(airline)

    return Response(serializer.data)


@api_view(["GET"])
def search_flights(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    flights = Flight.objects.exclude(status__in=[1, 5])

    if status > 0:
        flights = flights.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        flights = flights.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        flights = flights.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = FlightsSerializer(flights, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_flight_by_id(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)
    serializer = FlightSerializer(flight, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_flight(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)
    serializer = FlightSerializer(flight, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)

    if flight.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    flight.status = 2
    flight.date_formation = timezone.now()
    flight.save()

    serializer = FlightSerializer(flight, many=False)

    return Response(serializer.data)


def random_date():
    now = datetime.now(tz=timezone.utc)
    return now + timedelta(random.uniform(0, 1) * 100)


@api_view(["PUT"])
def update_status_admin(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    flight = Flight.objects.get(pk=flight_id)

    if flight.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        flight.date = random_date()

    flight.date_complete = timezone.now()
    flight.status = request_status
    flight.moderator = get_moderator()
    flight.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_flight(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)

    if flight.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    flight.status = 5
    flight.save()

    serializer = FlightSerializer(flight, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_airline_from_flight(request, flight_id, airline_id):
    if not AirlineFlight.objects.filter(flight_id=flight_id, airline_id=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = AirlineFlight.objects.get(flight_id=flight_id, airline_id=airline_id)
    item.delete()

    items = AirlineFlight.objects.filter(flight_id=flight_id)
    data = [AirlineItemSerializer(item.airline, context={"count": item.count}).data for item in items]

    return Response(data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_airline_in_flight(request, flight_id, airline_id):
    if not AirlineFlight.objects.filter(airline_id=airline_id, flight_id=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = AirlineFlight.objects.get(airline_id=airline_id, flight_id=flight_id)

    serializer = AirlineFlightSerializer(item, data=request.data,  partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)