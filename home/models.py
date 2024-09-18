# roomio/home/models.py
from django.db import models
from add_post.models import ApartmentUnit
from login.models import User
from django.conf import settings



class Interest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    unit = models.ForeignKey(ApartmentUnit, on_delete=models.CASCADE)
    roommate_count = models.PositiveSmallIntegerField()
    move_in_date = models.DateField()

    

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_favorites')
    # unit = models.ForeignKey(ApartmentUnit, on_delete=models.CASCADE, related_name='unit_favorites',default=ApartmentUnit.objects.first().id)
    unit = models.ForeignKey(ApartmentUnit, on_delete=models.CASCADE, related_name='unit_favorites')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'unit')
    