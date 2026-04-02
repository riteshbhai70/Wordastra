from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Count, Sum
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
            return redirect('home')
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
                update_session_auth_hash(request, user)
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

    # Use a single aggregated query instead of N+1 loops
    user_blogs = BlogPost.objects.filter(author=request.user).order_by('-created_at').annotate(
        comment_count=Count('comments', distinct=True),
        like_count=Count('likes', distinct=True),
    )

    aggregates = user_blogs.aggregate(
        total_likes=Sum('like_count'),
        total_comments=Sum('comment_count'),
    )

    recent_comments = Comment.objects.filter(
        post__author=request.user
    ).select_related('author', 'post').order_by('-created_at')[:10]

    context = {
        'user': request.user,
        'user_blogs': user_blogs,
        'total_blogs': user_blogs.count(),
        'total_likes': aggregates['total_likes'] or 0,
        'total_comments': aggregates['total_comments'] or 0,
        'current_time': timezone.now(),
        'recent_comments': recent_comments,
    }
    return render(request, 'users/dashboard.html', context)

