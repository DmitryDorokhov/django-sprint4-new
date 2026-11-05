from django import forms
from django.core.exceptions import ValidationError

from blog.models import Comment, Post
from blog.moderation import is_toxic

MODERATION_ERROR = (
    "Комментарий не проходит модерацию. "
    "Пожалуйста, сформулируйте мысль корректнее."
)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        text = self.cleaned_data.get('text') if self.cleaned_data else None
        if text and is_toxic(text):
            raise ValidationError(MODERATION_ERROR)
        return text


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
        }
