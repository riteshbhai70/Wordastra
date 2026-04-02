from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from PIL import Image
import os


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    content = models.TextField()
    excerpt = models.CharField(max_length=300, blank=True)
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts', db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.IntegerField(default=1, db_index=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    views = models.IntegerField(default=0)

    class Meta:
        db_table = 'blog_posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['published', '-created_at']),
            models.Index(fields=['author', 'published']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        # Auto-generate excerpt from content if not provided
        if not self.excerpt and self.content:
            words = self.content.split()
            self.excerpt = ' '.join(words[:30]) + ('…' if len(words) > 30 else '')

        super().save(*args, **kwargs)

        # Resize image after saving
        if self.featured_image:
            try:
                img_path = self.featured_image.path
                img = Image.open(img_path)
                if img.height > 800 or img.width > 1200:
                    output_size = (1200, 800)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    img.save(img_path, quality=85, optimize=True)
            except Exception:
                pass

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

    def total_likes(self):
        return self.likes.count()

    def reading_time(self):
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))


class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_comments', blank=True)

    class Meta:
        db_table = 'comments'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

    def total_likes(self):
        return self.likes.count()

    @property
    def is_reply(self):
        return self.parent is not None
