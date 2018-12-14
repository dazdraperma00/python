from django.forms import ModelForm, HiddenInput
from blogs_platform.models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['subject', 'text']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['author_nick', 'text', 'post']
        widgets = {
            'post': HiddenInput()
        }
