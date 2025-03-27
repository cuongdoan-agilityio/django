from django.views.generic import ListView, FormView, UpdateView
from posts.models.post import Post
from posts.forms import PostForm


class PostListView(ListView):
    """
    PostListView
    """

    template_name = "posts/list.html"
    model = Post
    context_object_name = "post_list"

    def get_queryset(self):
        return Post.objects.all().order_by("-updated_at")


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
