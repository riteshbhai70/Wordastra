from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import BlogPost, Comment

User = get_user_model()

class BlogCommentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.post = BlogPost.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user,
            published=1,
        )

    def test_comment_post_field_has_no_default_and_relates_to_author(self):
        comment = Comment.objects.create(post=self.post, author=self.user, content='Nice post!')

        self.assertEqual(comment.post, self.post)
        qs = Comment.objects.filter(post__author=self.user)
        self.assertIn(comment, qs)

    def test_dashboard_view_authenticated_user(self):
        client = Client()
        login = client.login(username='testuser', password='password123')
        self.assertTrue(login)

        response = client.get(reverse('dashboard'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

        Comment.objects.create(post=self.post, author=self.user, content='Comment for dashboard')
        response = client.get(reverse('dashboard'), secure=True)
        self.assertContains(response, 'Comment for dashboard')
