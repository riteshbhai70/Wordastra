from django.utils import timezone

def current_time(request):
    context = {'current_time': timezone.now()}
    if request.user.is_authenticated:
        from blogs.models import Comment
        recent_comments = Comment.objects.filter(post__author=request.user).order_by('-created_at')[:5]
        context['recent_notifications'] = recent_comments
        context['notification_count'] = recent_comments.count()
    else:
        context['recent_notifications'] = []
        context['notification_count'] = 0
    return context