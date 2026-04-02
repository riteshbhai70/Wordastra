from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'profile_completed', 'is_staff', 'last_login_time', 'is_active_session']
    list_filter = ['role', 'profile_completed', 'is_staff', 'is_superuser', 'is_active', 'is_active_session']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Clerk Info', {'fields': ('clerk_user_id', 'profile_image', 'bio')}),
        ('Session Info', {'fields': ('last_login_time', 'session_start', 'is_active_session')}),
        ('Profile', {'fields': ('role', 'profile_completed')}),
    )
