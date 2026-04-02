from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, F
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.conf import settings
from .models import BlogPost, Comment
from .forms import BlogPostForm, CommentForm


def _reading_time(content):
    """Estimate reading time in minutes (avg 200 words/min)."""
    word_count = len(content.split())
    minutes = max(1, round(word_count / 200))
    return minutes


def home(request):
    try:
        query = request.GET.get('q', '')
        if query:
            blogs = BlogPost.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query),
                published=1
            ).select_related('author').annotate(
                comment_count=Count('comments', distinct=True),
                like_count=Count('likes', distinct=True),
            )
        else:
            blogs = BlogPost.objects.filter(published=1).select_related('author').annotate(
                comment_count=Count('comments', distinct=True),
                like_count=Count('likes', distinct=True),
            )

        paginator = Paginator(blogs, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {'blogs': page_obj, 'query': query, 'page_obj': page_obj}
        return render(request, 'blogs/home.html', context)
    except Exception as e:
        import logging
        logging.error(f"Error in home view: {e}")
        return render(request, 'blogs/home.html', {'blogs': [], 'query': '', 'error': str(e)})


def blog_detail(request, slug):
    blog = get_object_or_404(
        BlogPost.objects.select_related('author').prefetch_related(
            'comments__author', 'comments__replies__author', 'likes'
        ),
        slug=slug,
    )
    # Use F() to avoid race conditions when incrementing views
    BlogPost.objects.filter(pk=blog.pk).update(views=F('views') + 1)
    blog.views += 1  # keep local object in sync for display

    comments = blog.comments.filter(parent=None).select_related('author').prefetch_related(
        'replies__author', 'likes', 'replies__likes'
    )
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
        liked_comment_ids = set(
            Comment.objects.filter(post=blog, likes=request.user).values_list('id', flat=True)
        )
    else:
        liked_comment_ids = set()

    reading_time = _reading_time(blog.content)

    context = {
        'blog': blog,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': blog.likes.filter(id=request.user.id).exists() if request.user.is_authenticated else False,
        'liked_comment_ids': liked_comment_ids,
        'reading_time': reading_time,
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
            messages.success(request, 'Blog post created successfully!')
            return redirect('blog_detail', slug=blog.slug)
    else:
        form = BlogPostForm()

    return render(request, 'blogs/blog_form.html', {'form': form, 'action': 'Create'})


@login_required
def blog_edit(request, slug):
    blog = get_object_or_404(BlogPost, slug=slug)

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
    blog = get_object_or_404(BlogPost, slug=slug)

    if blog.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this blog.')
        return redirect('blog_detail', slug=slug)

    if request.method == 'POST':
        blog.delete()
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
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
        }, status=500)


@login_required
def blog_like(request, slug):
    blog = get_object_or_404(BlogPost, slug=slug)

    if blog.likes.filter(id=request.user.id).exists():
        blog.likes.remove(request.user)
        messages.info(request, 'Blog unliked.')
    else:
        blog.likes.add(request.user)
        messages.success(request, 'Blog liked!')

    return redirect('blog_detail', slug=slug)


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment.objects.select_related('post', 'author'), id=comment_id)

    if comment.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('blog_detail', slug=comment.post.slug)

    blog_slug = comment.post.slug
    comment.delete()
    messages.success(request, 'Comment deleted successfully!')
    return redirect('blog_detail', slug=blog_slug)


@login_required
def comment_like(request, comment_id):
    comment = get_object_or_404(Comment.objects.select_related('post'), id=comment_id)

    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)
        messages.info(request, 'Comment unliked.')
    else:
        comment.likes.add(request.user)
        messages.success(request, 'Comment liked!')

    return redirect('blog_detail', slug=comment.post.slug)


@login_required
def comment_reply(request, comment_id):
    parent_comment = get_object_or_404(Comment.objects.select_related('post'), id=comment_id)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(
                post=parent_comment.post,
                author=request.user,
                content=content,
                parent=parent_comment,
            )
            messages.success(request, 'Reply added successfully!')
        else:
            messages.error(request, 'Reply content cannot be empty.')

    return redirect('blog_detail', slug=parent_comment.post.slug)


def robots_txt(request):
    from django.http import HttpResponse
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /users/",
        "Disallow: /api/",
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
