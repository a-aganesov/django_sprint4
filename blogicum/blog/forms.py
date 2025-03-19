from django import forms

from .models import Post, User, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ("author",)


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ("text",)


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
