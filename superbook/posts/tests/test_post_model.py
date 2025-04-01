from django.test import TestCase
from posts.models.post import Post

from posts.factories import PostFactory, SuperHeroFactory


class PostModelTest(TestCase):
    """
    Test the Post model.
    """

    def setUp(self):
        self.hero = SuperHeroFactory(name="Superman")
        self.active_post = PostFactory(
            hero=self.hero, content="This is an active post", likes=10
        )
        self.inactive_post = PostFactory(
            hero=self.hero, content="This is deactivate", likes=5
        )

    def test_post_str_method(self):
        self.assertEqual(str(self.active_post), "Superman: This is an active post")

    def test_active_post_manager(self):
        active_posts = Post.active_objects.all()
        self.assertIn(self.active_post, active_posts)
        self.assertNotIn(self.inactive_post, active_posts)

    def test_active_post_manager_empty_queryset(self):
        """
        Test that ActivePostManager returns an empty queryset if no posts match the filter.
        """

        self.active_post.delete()
        active_posts = Post.active_objects.all()
        self.assertEqual(active_posts.count(), 0)
