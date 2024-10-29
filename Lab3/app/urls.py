from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/airlines/', search_airlines),  # GET
    path('api/airlines/<int:airline_id>/', get_airline_by_id),  # GET
    path('api/airlines/<int:airline_id>/update/', update_airline),  # PUT
    path('api/airlines/<int:airline_id>/update_image/', update_airline_image),  # POST
    path('api/airlines/<int:airline_id>/delete/', delete_airline),  # DELETE
    path('api/airlines/create/', create_airline),  # POST
    path('api/airlines/<int:airline_id>/add_to_flight/', add_airline_to_flight),  # POST

    # Набор методов для заявок
    path('api/flights/', search_flights),  # GET
    path('api/flights/<int:flight_id>/', get_flight_by_id),  # GET
    path('api/flights/<int:flight_id>/update/', update_flight),  # PUT
    path('api/flights/<int:flight_id>/update_status_user/', update_status_user),  # PUT
    path('api/flights/<int:flight_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/flights/<int:flight_id>/delete/', delete_flight),  # DELETE

    # Набор методов для м-м
    path('api/flights/<int:flight_id>/update_airline/<int:airline_id>/', update_airline_in_flight),  # PUT
    path('api/flights/<int:flight_id>/delete_airline/<int:airline_id>/', delete_airline_from_flight),  # DELETE

    # Набор методов пользователей
    path('api/users/register/', register), # POST
    path('api/users/login/', login), # POST
    path('api/users/logout/', logout), # POST
    path('api/users/<int:user_id>/update/', update_user) # PUT
]
