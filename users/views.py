from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from .forms import UserRegisterForm, UserLoginForm, ProfileUpdateForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('home')
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
        'CLERK_PUBLISHABLE_KEY': settings.CLERK_PUBLISHABLE_KEY,
        'CLERK_FRONTEND_API': settings.CLERK_FRONTEND_API,
    }
    return render(request, 'users/register.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            user.last_login_time = timezone.now()
            user.session_start = timezone.now()
            user.is_active_session = True
            user.save()
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')  # Temporarily redirect to home instead of dashboard
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()

    context = {
        'form': form,
        'CLERK_PUBLISHABLE_KEY': settings.CLERK_PUBLISHABLE_KEY,
        'CLERK_FRONTEND_API': settings.CLERK_FRONTEND_API,
    }
    return render(request, 'users/login.html', context)


def logout_view(request):
    if request.user.is_authenticated:
        user = request.user
        user.is_active_session = False
        user.save()
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
            else:
                messages.error(request, 'Error updating profile.')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Password changed successfully!')
                return redirect('profile')
            else:
                messages.error(request, 'Error changing password.')
    else:
        profile_form = ProfileUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    context = {
        'user': request.user,
        'current_time': timezone.now(),
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'users/profile.html', context)


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    from blogs.models import BlogPost, Comment
    user_blogs = BlogPost.objects.filter(author=request.user).order_by('-created_at')
    recent_comments = Comment.objects.filter(post__author=request.user).order_by('-created_at')[:10]
    total_likes = sum(blog.likes.count() for blog in user_blogs)
    total_comments = sum(blog.comments.count() for blog in user_blogs)

    context = {
        'user': request.user,
        'user_blogs': user_blogs,
        'total_blogs': user_blogs.count(),
        'total_likes': total_likes,
        'total_comments': total_comments,
        'current_time': timezone.now(),
        'recent_comments': recent_comments,
    }
    return render(request, 'users/dashboard.html', context)

