from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MODERATOR = 'moderator', 'Moderator'
        AUTHOR = 'author', 'Author'
        VIEWER = 'viewer', 'Viewer'

    clerk_user_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    last_login_time = models.DateTimeField(null=True, blank=True)
    session_start = models.DateTimeField(null=True, blank=True)
    is_active_session = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.AUTHOR)
    profile_completed = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['clerk_user_id']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Mark profile as completed when essential fields are filled
        self.profile_completed = bool(
            self.first_name and self.last_name and self.email and self.bio
        )
        super().save(*args, **kwargs)
