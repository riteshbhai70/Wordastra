from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.conf import settings
from .models import BlogPost, Comment, Category, Tag
from .forms import BlogPostForm, CommentForm


def home(request):
    try:
        query = request.GET.get('q', '')
        category_slug = request.GET.get('category', '')
        tag_slug = request.GET.get('tag', '')
        sort = request.GET.get('sort', '-created_at')

        allowed_sorts = {
            'newest': '-created_at',
            'oldest': 'created_at',
            'popular': '-views',
            'liked': '-likes_count',
        }
        order_by = allowed_sorts.get(sort, '-created_at')

        blogs = (
            BlogPost.objects
            .filter(published=1, is_deleted=False)
            .select_related('author', 'category')
            .prefetch_related('likes', 'tags')
        )

        if query:
            blogs = blogs.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )

        if category_slug:
            blogs = blogs.filter(category__slug=category_slug)

        if tag_slug:
            blogs = blogs.filter(tags__slug=tag_slug)

        # Use F() expressions for safe ordering; avoid annotation for now
        if order_by in ('-created_at', 'created_at', '-views'):
            blogs = blogs.order_by(order_by)
        else:
            blogs = blogs.order_by('-created_at')

        featured_blogs = BlogPost.objects.filter(
            published=1, featured=True, is_deleted=False
        ).select_related('author')[:3]

        paginator = Paginator(blogs, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        categories = Category.objects.all()
        tags = Tag.objects.all()

        context = {
            'blogs': page_obj,
            'page_obj': page_obj,
            'query': query,
            'featured_blogs': featured_blogs,
            'categories': categories,
            'tags': tags,
            'current_sort': sort,
            'current_category': category_slug,
            'current_tag': tag_slug,
        }
        return render(request, 'blogs/home.html', context)
    except Exception as e:
        import logging
        logging.error(f"Error in home view: {e}")
        return render(request, 'blogs/home.html', {'blogs': [], 'query': '', 'error': str(e)})


def blog_detail(request, slug):
    blog = get_object_or_404(
        BlogPost.objects.select_related('author', 'category').prefetch_related('likes', 'tags', 'comments__author'),
        slug=slug,
        is_deleted=False,
    )
    # Increment views atomically
    BlogPost.objects.filter(pk=blog.pk).update(views=F('views') + 1)
    blog.refresh_from_db(fields=['views'])

    comments = blog.comments.filter(is_deleted=False).select_related('author').prefetch_related('likes', 'replies')
    comment_form = CommentForm()

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = blog
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('blog_detail', slug=slug)

    if request.user.is_authenticated:
        liked_comment_ids = list(
            Comment.objects.filter(post=blog, likes=request.user, is_deleted=False).values_list('id', flat=True)
        )
    else:
        liked_comment_ids = []

    # Related posts
    related_posts = BlogPost.objects.filter(
        published=1, is_deleted=False
    ).exclude(pk=blog.pk).select_related('author')
    if blog.category:
        related_posts = related_posts.filter(category=blog.category)
    related_posts = related_posts[:3]

    context = {
        'blog': blog,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': blog.likes.filter(id=request.user.id).exists() if request.user.is_authenticated else False,
        'liked_comment_ids': liked_comment_ids,
        'related_posts': related_posts,
    }
    return render(request, 'blogs/blog_detail.html', context)


@login_required
def blog_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            form.save_m2m()
            messages.success(request, 'Blog post created successfully!')
            return redirect('blog_detail', slug=blog.slug)
    else:
        form = BlogPostForm()

    return render(request, 'blogs/blog_form.html', {'form': form, 'action': 'Create'})


@login_required
def blog_edit(request, slug):
    blog = get_object_or_404(BlogPost, slug=slug, is_deleted=False)

    if blog.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this blog.')
        return redirect('blog_detail', slug=slug)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('blog_detail', slug=blog.slug)
    else:
        form = BlogPostForm(instance=blog)

    return render(request, 'blogs/blog_form.html', {'form': form, 'action': 'Edit', 'blog': blog})


@login_required
def blog_delete(request, slug):
    blog = get_object_or_404(BlogPost, slug=slug, is_deleted=False)

    if blog.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this blog.')
        return redirect('blog_detail', slug=slug)

    if request.method == 'POST':
        blog.soft_delete()
        messages.success(request, 'Blog post deleted successfully!')
        return redirect('home')

    return render(request, 'blogs/blog_confirm_delete.html', {'blog': blog})


def health_check(request):
    try:
        from django.db import connection
        connection.cursor()

        from django.contrib.auth import get_user_model
        User = get_user_model()
        user_count = User.objects.count()
        blog_count = BlogPost.objects.count()

        return JsonResponse({
            'status': 'ok',
            'database': 'connected',
            'users': user_count,
            'blogs': blog_count,
            'debug': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS,
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'debug': settings.DEBUG,
        }, status=500)


@login_required
def blog_like(request, slug):
    blog = get_object_or_404(BlogPost, slug=slug, is_deleted=False)

    if blog.likes.filter(id=request.user.id).exists():
        blog.likes.remove(request.user)
        liked = False
    else:
        blog.likes.add(request.user)
        liked = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'total_likes': blog.total_likes()})

    return redirect('blog_detail', slug=slug)


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, is_deleted=False)

    if comment.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('blog_detail', slug=comment.post.slug)

    blog_slug = comment.post.slug
    comment.soft_delete()
    messages.success(request, 'Comment deleted successfully!')
    return redirect('blog_detail', slug=blog_slug)


@login_required
def comment_like(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, is_deleted=False)

    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'total_likes': comment.total_likes()})

    return redirect('blog_detail', slug=comment.post.slug)


@login_required
def comment_reply(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id, is_deleted=False)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(
                post=parent_comment.post,
                author=request.user,
                content=content,
                parent=parent_comment
            )
            messages.success(request, 'Reply added successfully!')
        else:
            messages.error(request, 'Reply content cannot be empty.')

    return redirect('blog_detail', slug=parent_comment.post.slug)
