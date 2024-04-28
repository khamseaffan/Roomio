from django.urls import path
from . import views
from .views import like_interest

app_name = "home"

urlpatterns = [
    path("", views.home_page, name="home"),  
    path("logout/", views.logout, name="logout"), 
    path('unit/<str:unit_id>/', views.unit_details, name='view_detail'),
    path("interests/<int:interest_id>/like/", views.like_interest, name='like_interest'),  
<<<<<<< Updated upstream
    path("interests/<int:interest_id>/dislike/", views.dislike_interest, name='dislike_interest'),  
    path("unit/<str:unit_id>/create_interest/", views.create_interest, name="create_interest"),
=======
>>>>>>> Stashed changes
]