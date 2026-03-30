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
        # Clerk sets the session token in a cookie named '__session'
        clerk_session_token = request.COOKIES.get('__session')
        
        if clerk_session_token and not request.user.is_authenticated:
            try:
                headers = {
                    'Authorization': f'Bearer {settings.CLERK_SECRET_KEY}',
                    'Content-Type': 'application/json'
                }
                
                # Verify the session token
                response = requests.get(
                    f'https://api.clerk.com/v1/sessions/{clerk_session_token}/verify',
                    headers=headers
                )
                
                if response.status_code == 200:
                    session_data = response.json()
                    clerk_user_id = session_data.get('user_id')
                    
                    if clerk_user_id:
                        # Get user details
                        user_response = requests.get(
                            f'https://api.clerk.com/v1/users/{clerk_user_id}',
                            headers=headers
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
                print(f"Clerk auth error: {e}")
        
        response = self.get_response(request)
        return response
