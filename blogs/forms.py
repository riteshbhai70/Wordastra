from django import forms
from .models import BlogPost, Comment

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'featured_image', 'content', 'published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter blog title'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'id': 'image-upload'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 15}),
            'published': forms.Select(choices=[(1, 'Published'), (0, 'Draft')], attrs={'class': 'form-select'})
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your comment...'})
        }
