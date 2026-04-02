from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import BlogPost, Comment, Category, Tag

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

        response = client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

        Comment.objects.create(post=self.post, author=self.user, content='Comment for dashboard')
        response = client.get(reverse('dashboard'))
        self.assertContains(response, 'Comment for dashboard')


class CategoryTagTests(TestCase):
    def test_category_slug_auto_generated(self):
        category = Category.objects.create(name='Django Tips')
        self.assertEqual(category.slug, 'django-tips')

    def test_tag_slug_auto_generated(self):
        tag = Tag.objects.create(name='Python')
        self.assertEqual(tag.slug, 'python')


class BlogPostModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='author', email='author@example.com', password='password123')

    def test_blog_slug_auto_generated(self):
        post = BlogPost.objects.create(title='Hello World', content='Content here', author=self.user)
        self.assertEqual(post.slug, 'hello-world')

    def test_blog_slug_unique_on_duplicate_title(self):
        BlogPost.objects.create(title='Duplicate Title', content='Content', author=self.user)
        post2 = BlogPost.objects.create(title='Duplicate Title', content='Content 2', author=self.user)
        self.assertNotEqual(post2.slug, 'duplicate-title')
        self.assertTrue(post2.slug.startswith('duplicate-title'))

    def test_soft_delete_blog(self):
        post = BlogPost.objects.create(title='To Delete', content='Content', author=self.user)
        self.assertFalse(post.is_deleted)
        post.soft_delete()
        post.refresh_from_db()
        self.assertTrue(post.is_deleted)
        self.assertIsNotNone(post.deleted_at)

    def test_soft_delete_comment(self):
        post = BlogPost.objects.create(title='Post', content='Content', author=self.user)
        comment = Comment.objects.create(post=post, author=self.user, content='Test comment')
        comment.soft_delete()
        comment.refresh_from_db()
        self.assertTrue(comment.is_deleted)

    def test_read_time_calculated(self):
        content = ' '.join(['word'] * 400)  # 400 words ~ 2 minutes
        post = BlogPost.objects.create(title='Long Post', content=content, author=self.user)
        self.assertEqual(post.read_time, 2)

    def test_home_view_excludes_soft_deleted(self):
        BlogPost.objects.create(title='Active Post', content='Content', author=self.user, published=1)
        deleted = BlogPost.objects.create(title='Deleted Post', content='Content', author=self.user, published=1)
        deleted.soft_delete()

        client = Client()
        response = client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Active Post')
        self.assertNotContains(response, 'Deleted Post')

    def test_home_view_pagination(self):
        for i in range(12):
            BlogPost.objects.create(title=f'Post {i}', content='Content', author=self.user, published=1)

        client = Client()
        response = client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        # Should be paginated with 9 per page
        self.assertIn('page_obj', response.context)

    def test_home_view_search(self):
        BlogPost.objects.create(title='Django Tutorial', content='Content about Django', author=self.user, published=1)
        BlogPost.objects.create(title='Python Guide', content='Content about Python', author=self.user, published=1)

        client = Client()
        response = client.get(reverse('home') + '?q=Django')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Tutorial')
        self.assertNotContains(response, 'Python Guide')

    def test_blog_like_toggle(self):
        post = BlogPost.objects.create(title='Liked Post', content='Content', author=self.user, published=1)
        client = Client()
        client.login(username='author', password='password123')

        # Like
        response = client.post(reverse('blog_like', kwargs={'slug': post.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(post.likes.filter(id=self.user.id).exists())

        # Unlike
        client.post(reverse('blog_like', kwargs={'slug': post.slug}))
        self.assertFalse(post.likes.filter(id=self.user.id).exists())


class UserModelTests(TestCase):
    def test_user_role_default(self):
        user = User.objects.create_user(username='newuser', password='pass123')
        self.assertEqual(user.role, 'author')

    def test_profile_completed_false_by_default(self):
        user = User.objects.create_user(username='incomplete', password='pass123')
        self.assertFalse(user.profile_completed)

    def test_profile_completed_true_when_fields_filled(self):
        user = User.objects.create_user(
            username='complete',
            password='pass123',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
        )
        user.bio = 'My bio'
        user.save()
        self.assertTrue(user.profile_completed)


class APITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', email='api@example.com', password='password123')
        self.client = Client()

    def test_api_blog_list_returns_only_published_public(self):
        BlogPost.objects.create(title='Public Post', content='Content', author=self.user, published=1, visibility='public')
        BlogPost.objects.create(title='Private Post', content='Content', author=self.user, published=1, visibility='private')
        BlogPost.objects.create(title='Deleted Post', content='Content', author=self.user, published=1, is_deleted=True)

        response = self.client.get('/api/blogs/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        titles = [item['title'] for item in data.get('results', data)]
        self.assertIn('Public Post', titles)
        self.assertNotIn('Private Post', titles)
        self.assertNotIn('Deleted Post', titles)

    def test_api_blog_search(self):
        BlogPost.objects.create(title='Unique Keyword Post', content='Content', author=self.user, published=1, visibility='public')
        response = self.client.get('/api/blogs/?search=Unique+Keyword')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        titles = [item['title'] for item in data.get('results', data)]
        self.assertIn('Unique Keyword Post', titles)

    def test_api_categories_endpoint(self):
        Category.objects.create(name='Tech')
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, 200)

    def test_api_tags_endpoint(self):
        Tag.objects.create(name='Django')
        response = self.client.get('/api/tags/')
        self.assertEqual(response.status_code, 200)


class ClerkWebhookTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_webhook_creates_user_on_user_created_event(self):
        import json
        payload = {
            'type': 'user.created',
            'data': {
                'id': 'clerk_123',
                'email_addresses': [{'email_address': 'webhook@example.com'}],
                'first_name': 'Webhook',
                'last_name': 'User',
            }
        }
        response = self.client.post(
            reverse('clerk_webhook'),
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(clerk_user_id='clerk_123').exists())

    def test_webhook_deactivates_user_on_user_deleted_event(self):
        import json
        user = User.objects.create_user(username='todelete', password='pass', clerk_user_id='clerk_456')
        payload = {
            'type': 'user.deleted',
            'data': {'id': 'clerk_456'},
        }
        response = self.client.post(
            reverse('clerk_webhook'),
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_active)
