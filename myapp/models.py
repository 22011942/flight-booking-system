from django.db import models
from django.core.validators import MinValueValidator

   
class Plane(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    
    def __str__(self):
        return self.name
    
    def seats_availible(self):
        booked_seats = Booking.objects.filter(schedule__route__plane=self).count()
        return self.capacity - booked_seats > 0
        

class Route(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    plane = models.ForeignKey(Plane, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return self.name
    
class booked_flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    departure_datetime = models.DateTimeField()
    capacity = models.IntegerField(validators=[MinValueValidator(0)])
    
    def __str__(self):
        return f"{self.route.name} - {self.departure_datetime}"
    

class WeeklySchedule(models.Model):
    DAYS = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
        (7, 'Every week day'),
    ]
    TIMEZONES = [
        ('GMT+12', 'GMT+12'),
        ('GMT+12:45', 'GMT+12:45'),
        ('GMT+10', 'GMT+10')
    ]
    
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAYS) 
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    departure_timezone = models.CharField(max_length=20, choices=TIMEZONES, default='GMT+12')
    arrival_timezone = models.CharField(max_length=20, choices=TIMEZONES, default='GMT+12')
    is_return_flight = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.route.name} -{self.day_of_week} - {self.departure_time} to {self.arrival_time}"


class Booking(models.Model):
    schedule = models.ForeignKey(WeeklySchedule, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    booking_reference = models.CharField(max_length=10, unique=True)
    canceled = models.BooleanField(default=False)
    booked_flight = models.ForeignKey(booked_flight, on_delete=models.CASCADE, null=True)
    
    class Meta:
        verbose_name_plural = "List of Reservations"
    
    def __str__(self):
        return str(f"{self.booking_reference} - {self.first_name} {self.last_name}")