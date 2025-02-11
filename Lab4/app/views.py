import random
from datetime import datetime, timedelta
import uuid

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

#from app.services.qr_generate import generate_flight_qr

from .permissions import *
from .redis import session_storage
from .serializers import *
from .utils import identity_user, get_session


def get_draft_flight(request):
    user = identity_user(request)

    if user is None:
        return None

    flight = Flight.objects.filter(owner=user).filter(status=1).first()

    return flight


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'airline_name',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)

#4.1.1. GET Получение всех авиакомпаний
#Метод GET для получения списка всех авиакомпаний с фильтрацией по имени
#Доступно всем пользователям

@api_view(["GET"])
def search_airlines(request):
    airline_name = request.GET.get("airline_name", "")

    airlines = Airline.objects.filter(status=1)

    if airline_name:
        airlines = airlines.filter(name__icontains=airline_name)

    serializer = AirlinesSerializer(airlines, many=True)

    draft_flight = get_draft_flight(request)

    resp = {
        "airlines": serializer.data,
        "airlines_count": AirlineFlight.objects.filter(flight=draft_flight).count() if draft_flight else None,
        "draft_flight_id": draft_flight.pk if draft_flight else None
    }

    return Response(resp)

#Этот декоратор ограничивает доступ только для пользователей с определенной ролью 
#Он проверяет, имеет ли пользователь права на выполнение действия

#4.1.2. POST Добавляет авиакомпанию в черновой авиарейс
#Доступно только модераторам

@api_view(["POST"])
@permission_classes([IsModerator])
def create_airline(request):
    serializer = AirlineSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Airline.objects.create(**serializer.validated_data)

    airlines = Airline.objects.filter(status=1)
    serializer = AirlineSerializer(airlines, many=True)

    return Response(serializer.data)

#4.1.3. GET Получbnm информацию об авиакомпании
#Метод GET для получения информации о конкретной авиакомпании по ее ID
#Доступно всем пользователям

@api_view(["GET"])
def get_airline_by_id(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)
    serializer = AirlineSerializer(airline)

    return Response(serializer.data)

#4.1.4. PUT Изменить данные авиакомпании (кроме картинки)
#Доступ только для модераторов

@api_view(["PUT"])
@permission_classes([IsModerator])
def update_airline(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)

    serializer = AirlineSerializer(airline, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)

#4.1.5. DELETE Удалить авиакомпанию
#Метод DELETE для удаления (или деактивации) авиакомпании
#Доступ только для модераторов

@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_airline(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)
    airline.status = 2
    airline.save()

    airline = Airline.objects.filter(status=1)
    serializer = AirlineSerializer(airline, many=True)

    return Response(serializer.data)

#4.1.6. POST Добавить авиакомпанию в авиарейс
#Метод POST для добавления авиакомпании в текущий авиарейс (черновик)
#Доступ только для аутентифицированных пользователей

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_airline_to_flight(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)

    draft_flight = get_draft_flight(request)

    if draft_flight is None:
        draft_flight = Flight.objects.create()
        draft_flight.date_created = timezone.now()
        draft_flight.owner = identity_user(request)
        draft_flight.save()

    if AirlineFlight.objects.filter(flight=draft_flight, airline=airline).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = AirlineFlight.objects.create()
    item.flight = draft_flight
    item.airline = airline
    item.save()

    serializer = FlightSerializer(draft_flight)
    return Response(serializer.data["airlines"])

#4.1.7. POST Изменение/добавление картинки авиакомпании
#Метод POST для изменения или добавления картинки авиакомпании
#Доступ только для модераторов

@api_view(["POST"])
@permission_classes([IsModerator])
def update_airline_image(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    airline.image = image
    airline.save()

    serializer = AirlineSerializer(airline)

    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'date_formation_start',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'date_formation_end',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)

#4.1.8. GET Получить все авиарейсы
#Метод GET для получения всех авиарейсов с фильтрацией по статусу и дате

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_flights(request):
    status_id = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    flights = Flight.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        flights = flights.filter(owner=user)

    if status_id > 0:
        flights = flights.filter(status=status_id)

    if date_formation_start and parse_datetime(date_formation_start):
        flights = flights.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        flights = flights.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = FlightsSerializer(flights, many=True)

    return Response(serializer.data)

#4.1.9. GET Получить один авиарейс
#Метод GET для получения информации о конкретном авиарейсе по его ID

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_flight_by_id(request, flight_id):
    user = identity_user(request)

    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)

    if not user.is_superuser and flight.owner != user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = FlightSerializer(flight)

    return Response(serializer.data)

#4.1.10. PUT Изменить поля авиарейса
#Метод PUT для изменения полей авиарейса (обновление)
#Доступ только для авторизованным пользователям

@swagger_auto_schema(method='put', request_body=FlightSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_flight(request, flight_id):
    user = identity_user(request)

    if not Flight.objects.filter(pk=flight_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)
    serializer = FlightSerializer(flight, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

#4.1.11. DELETE Удалить авиарейс
#Метод DELETE для удаления (деактивации) авиарейса
#Доступ только для авторизованным пользователям

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_flight(request, flight_id):
    user = identity_user(request)

    if not Flight.objects.filter(pk=flight_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)

    if flight.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    flight.status = 5
    flight.save()

    return Response(status=status.HTTP_200_OK)

#4.1.12. PUT Сформировать авиарейс 
#Метод PUT для сохранения статуса авиарейса
#Доступ только для авторизованным пользователям

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, flight_id):
    user = identity_user(request)

    if not Flight.objects.filter(pk=flight_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)

    if flight.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    flight.status = 2
    flight.date_formation = timezone.now()
    flight.save()

    serializer = FlightSerializer(flight)

    return Response(serializer.data)


def random_date():
    now = datetime.now(tz=timezone.utc)
    return now + timedelta(random.uniform(0, 1) * 100)

#4.1.13. PUT Модерировать авиарейс
#Метод PUT для модерации авиарейса, для изменения статуса авиарейса на завершённый или отменённый
#Доступ только для модераторов

@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, flight_id):
    # Проверка, существует ли авиарейс
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    # Проверка, что статус корректен (3 - Завершен, 4 - Отклонен)
    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    flight = Flight.objects.get(pk=flight_id)

    # Проверка, что авиарейс находится в правильном статусе (В работе)
    if flight.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # Изменяем статус авиарейса и дату завершения
    flight.status = request_status
    flight.date_complete = timezone.now()
    flight.moderator = request.user  # Устанавливаем модератора как текущего пользователя
    flight.save()

    # Генерация QR-кода, если статус "Завершен"
    if flight.status == 3:
        qr_code = generate_flight_qr(flight)  # Генерация QR-кода
        if not qr_code:
            print("Ошибка: QR-код не сгенерировался!")
        flight.qr = qr_code

    # Обновляем данные
    flight.save()

    # Сериализация и возврат данных
    serializer = FlightSerializer(flight)
    return Response(serializer.data)

#4.1.14. DELETE Удалить авиакомпанию из авиарейса
#Метод DELETE для удаления авиакомпании из конкретного авиарейса
#Доступно только авторизованным пользователям

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_airline_from_flight(request, flight_id, airline_id):
    user = identity_user(request)

    if not Flight.objects.filter(pk=flight_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not AirlineFlight.objects.filter(flight_id=flight_id, airline_id=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = AirlineFlight.objects.get(flight_id=flight_id, airline_id=airline_id)
    item.delete()

    flight = Flight.objects.get(pk=flight_id)

    serializer = FlightSerializer(flight)
    airlines = serializer.data["airlines"]

    return Response(airlines)

#4.1.15. PUT Изменить авиарейс
#метод PUT Обновляет кол-во мест авиакомпании в авиарейсе 
#Доступно только авторизованным пользователям

@swagger_auto_schema(method='PUT', request_body=AirlineFlightSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_airline_in_flight(request, flight_id, airline_id):
    user = identity_user(request)

    if not Flight.objects.filter(pk=flight_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not AirlineFlight.objects.filter(airline_id=airline_id, flight_id=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = AirlineFlight.objects.get(airline_id=airline_id, flight_id=flight_id)

    serializer = AirlineFlightSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

#4.1.16. POST Регистрация
#Метод POST для регистрации нового пользователя
#Создаётся новый пользователь, создаётся сессия, и устанавливается cookie с идентификатором сессии
#Доступно только гостям

@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response

#4.1.17. PUT Обновляет данные пользователя
#Метод PUT для обновления информации о пользователе в его личном кабинете 
#(например, обновление email или пароля)
#Доступно только авторизованным пользователям

@swagger_auto_schema(method='PUT', request_body=UserProfileSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    password = request.data.get("password", None)
    if password is not None and not user.check_password(password):
        user.set_password(password)
        user.save()

    return Response(serializer.data, status=status.HTTP_200_OK)

#При аутентификации генерируется сессия и кладется в редис
#В качестве ключа – сгенерированная сессия
#В качестве значения ключа – id пользователя
#Также сессия сохраняется в куку session_id

#4.1.18. POST Аутентификация
#Метод POST для аутентификации пользователя
#Проверяются данные, если аутентификация прошла успешно,
#Cоздается сессия и отправляется cookie с идентификатором сессии
#Доступно всем 

@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    user = identity_user(request)

    if serializer.is_valid():
        user = authenticate(**serializer.data)
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        session_id = str(uuid.uuid4())
        session_storage.set(session_id, user.id)

        serializer = UserSerializer(user)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        response.set_cookie("session_id", session_id, samesite="lax")

        return response

    if user is not None:
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

#Во время деаутентификации сессия удаляется из редиса и из кук пользователя

#4.1.19. POST Деавторизация
#Метод POST для выхода пользователя из системы
#Сессия удаляется как из Redis, так и из cookies
#Доступно только авторизованным пользователям

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response