from django.views.generic import ListView, FormView, UpdateView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response

from posts.models.post import Post
from posts.forms import PostForm
from posts.serializers import PostSerializer
from posts.pagination import PostPagination


@method_decorator(cache_page(60), name="dispatch")
class PostListView(ListView):
    """
    PostListView
    """

    template_name = "posts/list.html"
    model = Post
    context_object_name = "post_list"
    cache_key = "post_list"


class PostView(generics.ListAPIView):
    """
    PostListView
    """

    queryset = Post.objects.all()
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    serializer_class = PostSerializer
    pagination_class = PostPagination
    cache_key = "post_list"
    ordering = "-updated_at"

    @method_decorator(cache_page(60, key_prefix="product_list"))
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            if request.accepted_renderer.format == "html":
                return Response({"post_list": page}, template_name="posts/list.html")

            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PostCreateView(FormView):
    """
    Post Create View
    """

    template_name = "posts/detail.html"
    form_class = PostForm
    context_object_name = "post"
    success_url = "/posts/"
    model = Post
    cache_key = "post_list"

    def form_valid(self, form):
        form.save()
        cache.delete("post_list")
        return super().form_valid(form)


class PostDetailView(UpdateView):
    """
    Post Detail View
    """

    template_name = "posts/detail.html"
    form_class = PostForm
    model = Post
    context_object_name = "post"
    success_url = "/posts/"

    def form_valid(self, form):
        response = super().form_valid(form)
        return response
