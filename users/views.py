import json
import hashlib
import hmac
import logging

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse

from .forms import UserRegisterForm, UserLoginForm, ProfileUpdateForm

logger = logging.getLogger(__name__)


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
    from django.db.models import Count, Q

    user_blogs = (
        BlogPost.objects
        .filter(author=request.user, is_deleted=False)
        .order_by('-created_at')
        .annotate(
            comment_count=Count('comments', filter=Q(comments__is_deleted=False)),
        )
    )
    recent_comments = (
        Comment.objects
        .filter(post__author=request.user, is_deleted=False)
        .select_related('author', 'post')
        .order_by('-created_at')[:10]
    )
    total_likes = sum(blog.likes.count() for blog in user_blogs)
    total_views = sum(blog.views for blog in user_blogs)
    total_comments = sum(blog.comments.filter(is_deleted=False).count() for blog in user_blogs)

    context = {
        'user': request.user,
        'user_blogs': user_blogs,
        'total_blogs': user_blogs.count(),
        'total_likes': total_likes,
        'total_comments': total_comments,
        'total_views': total_views,
        'current_time': timezone.now(),
        'recent_comments': recent_comments,
    }
    return render(request, 'users/dashboard.html', context)


@csrf_exempt
@require_POST
def clerk_webhook(request):
    """Handle Clerk webhook events for user synchronization."""
    webhook_secret = getattr(settings, 'CLERK_WEBHOOK_SECRET', '')

    if webhook_secret:
        svix_id = request.headers.get('svix-id', '')
        svix_timestamp = request.headers.get('svix-timestamp', '')
        svix_signature = request.headers.get('svix-signature', '')

        if not all([svix_id, svix_timestamp, svix_signature]):
            return HttpResponse('Missing Svix headers', status=400)

        to_sign = f"{svix_id}.{svix_timestamp}.{request.body.decode('utf-8')}"
        secret_bytes = webhook_secret.encode('utf-8')
        if webhook_secret.startswith('whsec_'):
            import base64
            secret_bytes = base64.b64decode(webhook_secret[6:])

        expected_sig = hmac.new(secret_bytes, to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        provided_signatures = [s.split(',', 1)[-1] for s in svix_signature.split(' ')]

        if not any(hmac.compare_digest(expected_sig, sig) for sig in provided_signatures):
            return HttpResponse('Invalid signature', status=400)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse('Invalid JSON', status=400)

    event_type = payload.get('type', '')
    data = payload.get('data', {})

    from django.contrib.auth import get_user_model
    User = get_user_model()

    if event_type in ('user.created', 'user.updated'):
        clerk_user_id = data.get('id', '')
        email_addresses = data.get('email_addresses', [])
        email = email_addresses[0].get('email_address', '') if email_addresses else ''
        first_name = data.get('first_name', '') or ''
        last_name = data.get('last_name', '') or ''
        profile_image_url = data.get('profile_image_url', '') or ''

        if clerk_user_id:
            user, created = User.objects.get_or_create(
                clerk_user_id=clerk_user_id,
                defaults={
                    'username': email.split('@')[0] if email else clerk_user_id,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )
            if not created:
                user.email = email or user.email
                user.first_name = first_name or user.first_name
                user.last_name = last_name or user.last_name
                user.save()
            logger.info('Clerk webhook: user %s %s', 'created' if created else 'updated', clerk_user_id)

    elif event_type == 'user.deleted':
        clerk_user_id = data.get('id', '')
        if clerk_user_id:
            User.objects.filter(clerk_user_id=clerk_user_id).update(is_active=False)
            logger.info('Clerk webhook: user deactivated %s', clerk_user_id)

    return HttpResponse(status=200)

