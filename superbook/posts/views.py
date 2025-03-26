from django.views.generic import ListView
from posts.models.post import Post


class PostListView(ListView):
    """
    PostListView
    """

    template_name = "posts/list.html"
    model = Post
    context_object_name = "post_list"

    def get_queryset(self):
        return Post.objects.all().order_by("-updated_at")
