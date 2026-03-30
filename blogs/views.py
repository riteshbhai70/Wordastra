from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import BlogPost, Comment
from .forms import BlogPostForm, CommentForm

def home(request):
    query = request.GET.get('q', '')
    if query:
        blogs = BlogPost.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            published=1  # Changed from True to 1
        )
    else:
        blogs = BlogPost.objects.filter(published=1)  # Changed from True to 1
    
    context = {'blogs': blogs, 'query': query}
    return render(request, 'blogs/home.html', context)

def blog_detail(request, slug):
    blog = get_object_or_404(BlogPost, slug=slug)
    blog.views += 1
    blog.save()
    
    comments = blog.comments.all()
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
        liked_comment_ids = list(Comment.objects.filter(post=blog, likes=request.user).values_list('id', flat=True))
    else:
        liked_comment_ids = []

    context = {
        'blog': blog,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': blog.likes.filter(id=request.user.id).exists() if request.user.is_authenticated else False,
        'liked_comment_ids': liked_comment_ids,
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

from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'ok'})

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
    comment = get_object_or_404(Comment, id=comment_id)
    
    if comment.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('blog_detail', slug=comment.post.slug)
    
    blog_slug = comment.post.slug
    comment.delete()
    messages.success(request, 'Comment deleted successfully!')
    return redirect('blog_detail', slug=blog_slug)

@login_required
def comment_like(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)
        messages.info(request, 'Comment unliked.')
    else:
        comment.likes.add(request.user)
        messages.success(request, 'Comment liked!')
    
    return redirect('blog_detail', slug=comment.post.slug)

@login_required
def comment_reply(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            reply = Comment.objects.create(
                post=parent_comment.post,
                author=request.user,
                content=content,
                parent=parent_comment
            )
            messages.success(request, 'Reply added successfully!')
        else:
            messages.error(request, 'Reply content cannot be empty.')
    
    return redirect('blog_detail', slug=parent_comment.post.slug)
