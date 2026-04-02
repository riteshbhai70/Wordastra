import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth import login

User = get_user_model()

class ClerkAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip middleware for certain paths
        if request.path.startswith('/admin/') or request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)

        # Clerk sets the session token in a cookie named '__session'
        clerk_session_token = request.COOKIES.get('__session')

        if clerk_session_token and not request.user.is_authenticated:
            try:
                # Only proceed if we have Clerk credentials
                if not settings.CLERK_SECRET_KEY:
                    return self.get_response(request)

                headers = {
                    'Authorization': f'Bearer {settings.CLERK_SECRET_KEY}',
                    'Content-Type': 'application/json'
                }

                # Verify the session token with correct API endpoint
                response = requests.post(
                    'https://api.clerk.com/v1/sessions/verify',
                    headers=headers,
                    json={'token': clerk_session_token},
                    timeout=5  # Add timeout
                )

                if response.status_code == 200:
                    session_data = response.json()
                    clerk_user_id = session_data.get('user_id')

                    if clerk_user_id:
                        # Get user details
                        user_response = requests.get(
                            f'https://api.clerk.com/v1/users/{clerk_user_id}',
                            headers=headers,
                            timeout=5
                        )

                        if user_response.status_code == 200:
                            user_data = user_response.json()
                            email = user_data.get('email_addresses', [{}])[0].get('email_address', '')
                            first_name = user_data.get('first_name', '')
                            last_name = user_data.get('last_name', '')
                            profile_image = user_data.get('profile_image_url', '')

                            user, created = User.objects.get_or_create(
                                clerk_user_id=clerk_user_id,
                                defaults={
                                    'username': email.split('@')[0] if email else clerk_user_id,
                                    'email': email,
                                    'first_name': first_name,
                                    'last_name': last_name,
                                    'profile_image': profile_image,
                                }
                            )

                            # Update user session info
                            user.last_login_time = timezone.now()
                            user.is_active_session = True
                            user.session_start = timezone.now()
                            user.save()

                            # Log the user in
                            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            except Exception as e:
                # Log error but don't break the request
                import logging
                logging.error(f"Clerk auth error: {e}")
                pass

        return self.get_response(request)
