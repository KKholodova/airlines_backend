from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('airlines/<int:airline_id>/', airline_details),
    path('airlines/<int:airline_id>/add_to_flight/', add_airline_to_draft_flight),
    path('flights/<int:flight_id>/delete/', delete_flight),
    path('flights/<int:flight_id>/', flight)
]
