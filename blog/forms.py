from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Post, Comment


User = get_user_model()


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=True,
    )

    class Meta:
        model = Post
        # exclude author; allow editing is_published and pub_date and all other fields
        exclude = ['author']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')
