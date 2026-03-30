from django.urls import path
from . import api_views

urlpatterns = [
    path('blogs/', api_views.BlogListAPIView.as_view(), name='api_blog_list'),
    path('blogs/<int:pk>/', api_views.BlogDetailAPIView.as_view(), name='api_blog_detail'),
]
