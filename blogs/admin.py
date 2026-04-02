from django.contrib import admin
from .models import BlogPost, Comment, Category, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'visibility', 'featured', 'published', 'created_at', 'views', 'is_deleted']
    list_filter = ['status', 'visibility', 'featured', 'published', 'is_deleted', 'created_at', 'author', 'category']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    filter_horizontal = ['tags', 'likes']
    readonly_fields = ['is_deleted', 'deleted_at', 'read_time']
    actions = ['make_featured', 'remove_featured', 'soft_delete_selected']

    def make_featured(self, request, queryset):
        queryset.update(featured=True)
    make_featured.short_description = 'Mark selected blogs as featured'

    def remove_featured(self, request, queryset):
        queryset.update(featured=False)
    remove_featured.short_description = 'Remove featured status'

    def soft_delete_selected(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_deleted=True, deleted_at=timezone.now())
    soft_delete_selected.short_description = 'Soft delete selected blogs'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at', 'is_deleted']
    list_filter = ['created_at', 'author', 'is_deleted']
    search_fields = ['content', 'author__username', 'post__title']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
