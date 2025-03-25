from posts.models.post import Post


class PostService:
    @staticmethod
    def create_post(hero, content):
        if hero.power != "None":
            return Post.objects.create(hero=hero, content=content)

        raise ValueError("Only supper heroes can create posts.")
