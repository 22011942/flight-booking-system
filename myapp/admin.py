from django.contrib import admin
from myapp.models import Route, Plane, WeeklySchedule, Booking, booked_flight
# Register your models here.

admin.site.register(Route)
admin.site.register(WeeklySchedule)
admin.site.register(Plane)
admin.site.register(Booking)
admin.site.register(booked_flight)