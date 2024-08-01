from django.shortcuts import render, redirect, get_object_or_404
from myapp.models import Route, WeeklySchedule, Booking, booked_flight
from datetime import datetime, timedelta
from django.utils.crypto import get_random_string


        
def route_search(request):
    routes = Route.objects.all()
    return render(request, 'frontpage.html', {'routes': routes})

def get_next_weekday(date, weekday):
    if weekday == 7:  
        while date.weekday() >= 5:  
            date += timedelta(days=1)
        return date
    else:
        days_ahead = weekday - date.weekday()
        if days_ahead < 0:
            days_ahead += 7
        elif days_ahead == 0:
            return date
        return date + timedelta(days_ahead)


def search_results(request):
    if request.method == 'GET':
        route_id = request.GET.get('route')
        departure_date_str = request.GET.get('departureDate')
        return_date_str = request.GET.get('returnDate')

        departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d').date()
        

        if return_date_str:
            return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()
        else:
            return_date = None


        route = get_object_or_404(Route, id=route_id)
        schedules = WeeklySchedule.objects.filter(route=route)
        departure_date_same = False
        return_date_same = False

        next_departure_date = None
        potential_departure_dates = []
        for schedule in schedules.filter(is_return_flight=False):
            potential_departure_dates.append((get_next_weekday(departure_date, schedule.day_of_week), schedule.id))
        
        next_departure_date, next_departure_schedule_id = min(potential_departure_dates, key=lambda x: x[0])
        if departure_date == next_departure_date:
            departure_date_same = True
        
        next_return_date = None
        potential_return_dates = []
        if return_date:
            for schedule in schedules.filter(is_return_flight=True):
                potential_return_dates.append((get_next_weekday(return_date, schedule.day_of_week), schedule.id))
            
            next_return_date, next_return_schedule_id = min(potential_return_dates, key=lambda x: x[0])
            if (return_date == next_return_date):
                return_date_same = True
        
        departure_seats_available = True
        departure_schedule = WeeklySchedule.objects.get(id=next_departure_schedule_id)
        departure_datetime = datetime.combine(next_departure_date, departure_schedule.departure_time)
        departure_booked_flight = booked_flight.objects.filter(
            route=route, 
            departure_datetime=departure_datetime
        ).first()
        
        if departure_booked_flight:
            if departure_booked_flight.capacity > 0:
                departure_seats_available = True
            else:
                departure_seats_available = False
                
        
        return_seats_available = True
        if return_date:
            return_schedule = WeeklySchedule.objects.get(id=next_return_schedule_id)
            return_datetime = datetime.combine(next_return_date, return_schedule.departure_time)
            return_booked_flight = booked_flight.objects.filter(
                route=route, 
                departure_datetime=return_datetime
            ).first()
            
            if return_booked_flight:
                if return_booked_flight.capacity > 0:
                    return_seats_available = True
                else:
                    return_seats_available = False

        if not departure_seats_available and (return_date and not return_seats_available):
            error = "No available seats for the selected dates."
            return render(request, 'search_results.html', {'route': route, 'error': error})
        elif not departure_seats_available:
            error = "No available seats for the selected departure date."
            return render(request, 'search_results.html', {'route': route, 'error': error})
        elif return_date and not return_seats_available:
            error = "No available seats for the selected return date."
            return render(request, 'search_results.html', {'route': route, 'error': error})

        return render(request, 'search_results.html', {
            'route': route, 
            'next_departure_date': next_departure_date, 
            'departure_date_same': departure_date_same,
            'next_return_date': next_return_date, 
            'return_date_same': return_date_same,
            'error': None, 
            'next_departure_schedule_id':next_departure_schedule_id, 
            'next_return_schedule_id': next_return_schedule_id if return_date else None})
        
def route_list(request):
    routes = Route.objects.all()
    return render(request, 'routes.html', {'routes': routes})

def schedule_list(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    outbound_flights = WeeklySchedule.objects.filter(route=route, is_return_flight=False)
    return_flights = WeeklySchedule.objects.filter(route=route, is_return_flight=True)
    
    departure_date_str = request.GET.get('departure_date', 'default_date') 

    return render(request, 'schedule.html', {
        'outbound_flights': outbound_flights,
        'return_flights': return_flights,
        'departure_date_str': departure_date_str
    })


def book_flight(request, schedule_id, departure_date_str, return_schedule_id=None, return_date_str=None):
    departure_schedule = get_object_or_404(WeeklySchedule, id=schedule_id)
    return_schedule = None  
    
    return_time_adjusted = None
    return_arrival_time_adjusted = None

    if return_schedule_id:
        return_schedule = get_object_or_404(WeeklySchedule, id=return_schedule_id)
        return_offset = get_timezone_offset(return_schedule.departure_timezone)
        return_arrival_offset = get_timezone_offset(return_schedule.arrival_timezone)
        return_time_adjusted = adjust_time(return_schedule.departure_time, return_offset)
        return_arrival_time_adjusted = adjust_time(return_schedule.arrival_time, return_arrival_offset)
    
    
    departure_offset = get_timezone_offset(departure_schedule.departure_timezone)
    arrival_offset = get_timezone_offset(departure_schedule.arrival_timezone)
    departure_time_adjusted = adjust_time(departure_schedule.departure_time, departure_offset)
    arrival_time_adjusted = adjust_time(departure_schedule.arrival_time, arrival_offset)
    
    departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d').date()
    departure_datetime = datetime.combine(departure_date, departure_schedule.departure_time)
            
    departure_booked_flight, departure_created = booked_flight.objects.get_or_create(
        route=departure_schedule.route,
        departure_datetime=departure_datetime,
        defaults={'capacity': departure_schedule.route.plane.capacity}
    )
    
    return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date() if return_date_str else None
    

    
    if return_schedule_id:
        return_schedule = get_object_or_404(WeeklySchedule, id=return_schedule_id)
        return_datetime = datetime.combine(return_date, return_schedule.departure_time)
        return_booked_flight, return_created = booked_flight.objects.get_or_create(
            route=return_schedule.route,
            departure_datetime=return_datetime,
            defaults={'capacity': return_schedule.route.plane.capacity}
        )
        

    if request.method == 'POST':
        
        if request.POST.get('book_flight_action') == 'book_flights':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            contact = request.POST.get('contact')


            departure_booking_reference = get_random_string(length=6)

    
            if not departure_created:
                departure_booked_flight.capacity -= 1
                departure_booked_flight.save()
            else:
                departure_booked_flight.capacity -= 1

            departure_booking = Booking.objects.create(
                schedule=departure_schedule,
                booking_reference=departure_booking_reference,
                first_name=first_name,
                last_name=last_name,
                email=email,
                contact=contact,
                booked_flight = departure_booked_flight
            )
            
            
            return_booking_reference = get_random_string(length=6)
            
            if return_schedule_id and return_date:
                if not return_created:
                    return_booked_flight.capacity -= 1
                    return_booked_flight.save()
                else: 
                    return_booked_flight.capacity -= 1

            if return_schedule:
                return_booking = Booking.objects.create(
                    schedule=return_schedule,
                    booking_reference=return_booking_reference,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    contact=contact,
                    booked_flight = return_booked_flight
                )
                

            if return_schedule:
                return redirect('booking_success_both', booking_reference=departure_booking_reference, return_booking_reference=return_booking_reference)
            else:
                return redirect('booking_success', booking_reference=departure_booking_reference)

    return render(request, 'book_flight.html', {
        'departure_schedule': departure_schedule,
        'return_schedule': return_schedule,
        'departure_booked_flight': departure_booked_flight,
        'return_booked_flight': return_booked_flight if return_schedule_id else None,
        'departure_time_adjusted': departure_time_adjusted,
        'arrival_time_adjusted': arrival_time_adjusted,
        'return_time_adjusted': return_time_adjusted if return_schedule_id else None,
        'departure_date': departure_date_str,
        'return_date': return_date_str,
        'return_arrival_time_adjusted': return_arrival_time_adjusted if return_schedule_id else None
    })
    
def get_timezone_offset(timezone):
    offsets = {
        'GMT+12': 0,
        'GMT+12:45': 0.75,
        'GMT+10': -2,
    }
    return offsets.get(timezone, 0)  

def adjust_time(time, offset):
    dt = datetime.combine(datetime.today(), time)
    adjusted_dt = dt + timedelta(hours=offset)
    return adjusted_dt.strftime('%H:%M')


def booking_success(request, booking_reference, return_booking_reference=None):
    booking = Booking.objects.get(booking_reference=booking_reference)
    
    departure_booking = booking
    return_booking = None
    departure_date = departure_booking.booked_flight.departure_datetime.date()
    departure_schedule = departure_booking.schedule
    
    
    departure_offset = get_timezone_offset(departure_schedule.departure_timezone)
    arrival_offset = get_timezone_offset(departure_schedule.arrival_timezone)
    departure_time_adjusted = adjust_time(departure_schedule.departure_time, departure_offset)
    arrival_time_adjusted = adjust_time(departure_schedule.arrival_time, arrival_offset)
    departure_timezone = departure_schedule.departure_timezone
    arrival_timezone = departure_schedule.arrival_timezone
    
    return_date = None
    if return_booking_reference:
        return_booking = Booking.objects.get(booking_reference=return_booking_reference)
        return_schedule = return_booking.schedule
        return_date = return_booking.booked_flight.departure_datetime.date()
        return_offset = get_timezone_offset(return_schedule.departure_timezone)
        return_arrival_offset = get_timezone_offset(return_schedule.arrival_timezone)
        return_time_adjusted = adjust_time(return_schedule.departure_time, return_offset)
        return_arrival_time_adjusted = adjust_time(return_schedule.arrival_time, return_arrival_offset)
        return_timezone = return_schedule.departure_timezone
        return_arrival_timezone = return_schedule.arrival_timezone

    return render(request, 'booking_success.html', {
        'departure_booking': departure_booking,
        'return_booking': return_booking,
        'departure_date': departure_date,
        'departure_time_adjusted': departure_time_adjusted,
        'arrival_time_adjusted': arrival_time_adjusted,
        'departure_timezone': departure_timezone,
        'arrival_timezone': arrival_timezone,
        'return_date': return_date if return_booking_reference else None,
        'return_time_adjusted': return_time_adjusted if return_booking_reference else None,
        'return_arrival_time_adjusted': return_arrival_time_adjusted if return_booking_reference else None,
        'return_timezone': return_timezone if return_booking_reference else None,
        'return_arrival_timezone': return_arrival_timezone if return_booking_reference else None,
    })

def get_day_of_week(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%A')

def cancel_confirm(request):
    error_message = None

    if request.method == 'POST':
        booking_reference = request.POST.get('booking_reference')
        
        try:
            booking = Booking.objects.get(booking_reference=booking_reference)
        except Booking.DoesNotExist:
            error_message = 'Booking does not exist.'
            return render(request, 'cancel_confirm.html', {'error_message': error_message})

        if booking.canceled:
            error_message = 'Booking has already been canceled.'
            return render(request, 'cancel_confirm.html', {'error_message': error_message})

        return redirect('cancel_booking', booking_reference=booking_reference)
    
    return render(request, 'cancel_confirm.html', {'error_message': error_message})
    

def cancel_booking(request, booking_reference):
    booking = get_object_or_404(Booking, booking_reference=booking_reference)
    
    departure_date = booking.booked_flight.departure_datetime.date()
    departure_schedule = booking.schedule
    
    departure_offset = get_timezone_offset(departure_schedule.departure_timezone)
    arrival_offset = get_timezone_offset(departure_schedule.arrival_timezone)
    departure_time_adjusted = adjust_time(departure_schedule.departure_time, departure_offset)
    arrival_time_adjusted = adjust_time(departure_schedule.arrival_time, arrival_offset)
    departure_timezone = departure_schedule.departure_timezone
    arrival_timezone = departure_schedule.arrival_timezone
    
    if request.method == 'POST':
        booking.canceled = True
        booking.save()
        booking.booked_flight.capacity += 1
        booking.booked_flight.save()
        
        return redirect('cancel_success', booking_reference=booking_reference)
    
    return render(request, 'cancel_booking.html', {
        'booking': booking,  
        'departure_date': departure_date,
        'departure_time_adjusted': departure_time_adjusted,
        'arrival_time_adjusted': arrival_time_adjusted,
        'departure_timezone': departure_timezone,
        'arrival_timezone': arrival_timezone,
    })


def cancel_success(request, booking_reference):
    booking = get_object_or_404(Booking, booking_reference=booking_reference)
    return render(request, 'cancel_success.html', {'booking': booking})
