from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    path("", views.home_page, name="home"),
    path("", views.logout, name="logout")
]