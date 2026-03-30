from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    clerk_user_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    last_login_time = models.DateTimeField(null=True, blank=True)
    session_start = models.DateTimeField(null=True, blank=True)
    is_active_session = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username
