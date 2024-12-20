from rest_framework import serializers

from .models import *


class AirlinesSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, airline):
        if airline.image:
            return airline.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Airline
        fields = ("id", "name", "status", "foundation_date", "image")


class AirlineSerializer(AirlinesSerializer):
    class Meta(AirlinesSerializer.Meta):
        fields = "__all__"


class FlightsSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Flight
        fields = "__all__"


class FlightSerializer(FlightsSerializer):
    airlines = serializers.SerializerMethodField()
            
    def get_airlines(self, flight):
        items = AirlineFlight.objects.filter(flight=flight)
        return [AirlineItemSerializer(item.airline, context={"count": item.count}).data for item in items]


class AirlineItemSerializer(AirlineSerializer):
    count = serializers.SerializerMethodField()

    def get_count(self, _):
        return self.context.get("count")

    class Meta:
        model = Airline
        fields = ("id", "name", "status", "foundation_date", "image", "count")


class AirlineFlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirlineFlight
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', "is_superuser")


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
