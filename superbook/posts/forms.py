from django import forms
from posts.models.post import Post
from crispy_forms.helper import FormHelper


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["hero", "content", "likes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
