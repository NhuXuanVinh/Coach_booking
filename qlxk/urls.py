from django.urls import path
from . import views

app_name = "qlxk"
urlpatterns = [
    path("", views.index, name="index"),
    path("signUp", views.signUp, name="signUp"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("user_trips", views.user_trips, name="user_trips"),
    path("<int:chuyenxe_id>/booking_seats", views.booking_seats, name="booking_seats"),
]