from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/create/', views.blog_create, name='blog_create'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/<slug:slug>/edit/', views.blog_edit, name='blog_edit'),
    path('blog/<slug:slug>/delete/', views.blog_delete, name='blog_delete'),
    path('blog/<slug:slug>/like/', views.blog_like, name='blog_like'),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('comment/<int:comment_id>/like/', views.comment_like, name='comment_like'),
    path('comment/<int:comment_id>/reply/', views.comment_reply, name='comment_reply'),
    path('health/', views.health_check, name='health_check'),
]
