from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('airlines/<int:airline_id>/', airline),
    path('flights/<int:flight_id>/', flight),
]