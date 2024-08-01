from django.urls import path
from . import views

urlpatterns = [
    path('frontpage', views.route_search, name='frontpage'),
    path('routes/', views.route_list, name='route_list'),
    path('schedules/<int:route_id>/', views.schedule_list, name='schedule_list'),
    path('book_flight/<int:schedule_id>/<str:departure_date_str>/', views.book_flight, name='book_flight'),
    path('book_flight/<int:schedule_id>/<int:return_schedule_id>/<str:departure_date_str>/<str:return_date_str>/', views.book_flight, name='book_flight_with_return'),
    path('myapp/booking_success/<str:booking_reference>/<str:return_booking_reference>/', views.booking_success, name='booking_success_both'),
    path('myapp/booking_success/<str:booking_reference>/', views.booking_success, name='booking_success'),
    path('cancel-booking/', views.cancel_confirm, name='cancel_confirm'),
    path('cancel/<str:booking_reference>/', views.cancel_booking, name='cancel_booking'),
    path('cancel_success/<str:booking_reference>/', views.cancel_success, name='cancel_success'),
    path('search_results/', views.search_results, name='search_results'),
]