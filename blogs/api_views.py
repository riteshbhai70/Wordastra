from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import BlogPost
from .serializers import BlogPostSerializer


class BlogListAPIView(generics.ListCreateAPIView):
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'views', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return BlogPost.objects.filter(published=1).select_related('author').prefetch_related('likes', 'comments')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BlogDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return BlogPost.objects.select_related('author').prefetch_related('likes', 'comments')
