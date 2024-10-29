from rest_framework import serializers

from .models import *


class AirlineSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, airline):
        return airline.image.url.replace("minio", "localhost", 1)

    class Meta:
        model = Airline
        fields = "__all__"


class AirlineItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    def get_image(self, airline):
        return airline.image.url.replace("minio", "localhost", 1)

    def get_value(self, airline):
        return self.context.get("value")

    class Meta:
        model = Airline
        fields = ("id", "name", "image", "value")


class FlightSerializer(serializers.ModelSerializer):
    airlines = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, flight):
        return flight.owner.username

    def get_moderator(self, flight):
        if flight.moderator:
            return flight.moderator.username
            
    def get_airlines(self, flight):
        items = AirlineFlight.objects.filter(flight=flight)
        return [AirlineItemSerializer(item.airline, context={"value": item.value}).data for item in items]

    class Meta:
        model = Flight
        fields = '__all__'


class FlightsSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, flight):
        return flight.owner.username

    def get_moderator(self, flight):
        if flight.moderator:
            return flight.moderator.username

    class Meta:
        model = Flight
        fields = "__all__"


class AirlineFlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirlineFlight
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
