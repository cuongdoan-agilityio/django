from django.views.generic import ListView, FormView, UpdateView
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response

from posts.models.post import Post
from posts.forms import PostForm
from posts.serializers import PostSerializer
from posts.pagination import PostPagination


class PostListView(ListView):
    """
    PostListView
    """

    template_name = "posts/list.html"
    model = Post
    context_object_name = "post_list"

    def get_queryset(self):
        return Post.objects.all().order_by("-updated_at")


class PostView(generics.ListCreateAPIView):
    """
    PostListView
    """

    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    serializer_class = PostSerializer
    pagination_class = PostPagination

    def get_queryset(self):
        return Post.objects.all().order_by("-updated_at")

    def get(self, request, *args, **kwargs):
        post_list = self.get_queryset()
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(post_list, request)

        if request.accepted_renderer.format == "html":
            return Response({"post_list": result_page}, template_name="posts/list.html")

        serializer = PostSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PostCreateView(FormView):
    """
    Post Create View
    """

    template_name = "posts/detail.html"
    form_class = PostForm
    context_object_name = "post"
    success_url = "/posts/"
    model = Post

    def form_valid(self, form):
        form.save()
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
