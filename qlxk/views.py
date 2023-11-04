from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .models import  Users, Xe, Chuyenxe, Nhanvienxe, Ghe, Ve,  Dieukhien, Datve, Danhgia
from django.db import connections
from django.db.models import Count, Q, Prefetch
import json
from django.contrib import messages
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Form for signing up
class signUpForm(forms.Form):
    username = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Username', "autocomplete": "off",'readonly': 'readonly',
    'onfocus': "this.removeAttribute('readonly');",
}))
    password = forms.CharField(max_length=64,widget=forms.PasswordInput(attrs={'placeholder': 'Password', "autocomplete": "off", 'readonly': 'readonly',
    'onfocus': "this.removeAttribute('readonly');",
}),)
    email =  forms.CharField(max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Your Email'}))
    sdt =  forms.CharField(max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Phone number'}))

    
# Main page
def index(request):
    has_find= False
    if request.method == "POST":
        # Get origin, destination and date
        has_find = True
        origin = request.POST.get("origin")
        destination = request.POST.get("destination")
        date = request.POST.get("date")
        # Find trips based on origin, destination and/or date
        if not date:
            chuyenxe = Chuyenxe.objects.filter(origin=origin, destination = destination)
        else:
            chuyenxe = Chuyenxe.objects.filter(origin=origin, destination=destination, chuyenxe_date = date)
        return render(request,"index.html",{
            "chuyenxe": chuyenxe,
            "has_find": has_find,
        })
    return render(request,"index.html",{
            "has_find": has_find,
        })

# Login
def login_view(request):
    if request.method == 'POST':
        # Get username and password
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('qlxk:index')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

# Logout
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("qlxk:index"))
    
def signUp(request):
    if request.method == "POST":
        newUser = signUpForm(request.POST)
        if newUser.is_valid():
            # Get user's info
            newusername = newUser.cleaned_data["username"]
            newpassword = newUser.cleaned_data["password"]
            newemail = newUser.cleaned_data["email"]
            newsdt = newUser.cleaned_data["sdt"]
            # Check if user's info are taken
            username_taken = Users.objects.raw("SELECT * FROM qlxk_users WHERE username = %s", [newusername])
            email_taken = Users.objects.raw("SELECT * FROM qlxk_users WHERE user_mail = %s", [newemail])
            sdt_taken = Users.objects.raw("SELECT * FROM qlxk_users WHERE user_phone = %s", [newsdt])
            # Error messages
            if username_taken:
                username_error = "Username taken!"
            if email_taken:
                email_error = "Email taken!"
            if sdt_taken:
                phone_error ="Phone number taken!"
            # If no infos taken, save user
            if  not username_taken and not email_taken and not sdt_taken:
                user = Users.objects.create_user(username=newusername, password=newpassword, user_mail=newemail, user_phone=newsdt)
                user.save()
                return HttpResponseRedirect(reverse("qlxk:login"))
        return render(request, "signUp.html", {
            "form": signUpForm(),
            "username_error": username_error,
            "email_error": email_error,
            "phone_error": phone_error,
        })  
    return render(request, "signUp.html", {
            "form": signUpForm(),
        })

# Show user's booked trips
def user_trips(request):
    # If user's not loged in, redirect to the login page
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("qlxk:login"))
    # Get user and their trips
    user = request.user
    chuyenxe_list = Chuyenxe.objects.filter(ve__datve__user_id=user).annotate(ticket_count=Count('ve'))
    return render(request, "user_trips.html",{
        "chuyenxe_list": chuyenxe_list,
        "haslogin": True,
    })


@csrf_exempt
def booking_seats(request, chuyenxe_id):
    # If user not log in redirect
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("qlxk:login"))
    
    # Get trip, bus, and user
    chuyenxe = Chuyenxe.objects.get(pk=chuyenxe_id)
    xe = chuyenxe.bien_so
    user_id = request.user
    has_booked = False
    
    # Get the numbers of seats in bus
    numCols = xe.column_number
    numRows = xe.row_number
    
    # User's already booked seats and other's booked seats
    blueSeats = []
    redSeats = []
    # Get all Ghe instances associated with the booked Ve instances
    myBooked_tickets = Ve.objects.filter(Q(datve__user_id=user_id) & Q(chuyenxe_id=chuyenxe_id))
    myBooked_seats = Ghe.objects.filter(ve__in=myBooked_tickets)
    # Get the booked seats number
    for myBooked_seat in myBooked_seats:
        blueSeats.append((myBooked_seat.row-1)*numCols+myBooked_seat.col)
    
    # Get booked seats by others
    booked_tickets = Ve.objects.filter(chuyenxe_id=chuyenxe_id, status=True).exclude(datve__user_id=user_id)
    booked_seats = Ghe.objects.filter(ve__in=booked_tickets)
    # Get the booked seats number
    for booked_seat in booked_seats:
        redSeats.append((booked_seat.row-1)*numCols+booked_seat.col)
        

    if request.method == 'POST':
        # Get seats data
        data = json.loads(request.body)
        selected_seats = data.get('selectedSeats', [])
        response_data = {}
        
        # Check if any seat is booked by other user
        for seat in selected_seats:
            # Get seats in row and column
            seat = int(seat)
            seat_row = (seat-1)//numCols+1
            seat_col = (seat-1)%numCols+1
            # Get seats and tickets accordingly
            seat_saved = Ghe.objects.get(bien_so=xe.bien_so,row=seat_row, col=seat_col)
            ve = Ve.objects.get(ghe_id=seat_saved.ghe_id, chuyenxe_id = chuyenxe_id)
            # If ve is booked by other users, return error
            if ve.status == True:
                has_booked = True
                messages.error(request, 'The selected seat is already booked.')
                response_data['message'] = 'The selected seat is already booked.'
                return JsonResponse(response_data)    
                
        # If not, save user booked tickets
        if not has_booked:
            for seat in selected_seats:
                seat = int(seat)
                seat_row = (seat-1)//numCols+1
                seat_col = (seat-1)%numCols+1
                seat_saved = Ghe.objects.get(bien_so=xe.bien_so,row=seat_row, col=seat_col)
                ve = Ve.objects.get(ghe_id=seat_saved.ghe_id, chuyenxe_id = chuyenxe_id)
                ve.status = True
                ve.save()
                booked = Datve(user_id = user_id, ve_id= ve)
                booked.save()
                response_data['message'] = 'Booking successful'
            return JsonResponse(response_data)

    return render(request, "seat.html",{
        "myBookedSeats": json.dumps(blueSeats),
        "bookedSeats": json.dumps(redSeats),
        "chuyenxe": chuyenxe,
        "numCols": numCols,
        "numRows": numRows,
    })

