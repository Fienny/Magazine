from django import forms
from django.core.exceptions import ValidationError

from .models import Post


class PostForm(forms.ModelForm):
    text = forms.CharField(min_length=20)

    class Meta:
        model = Post
        fields = [
            'author',
            'post_rating',
            'heading',
            'text',
        ]

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get("text")

        heading = cleaned_data.get('heading')
        if heading == text:
            raise ValidationError(
                "Описание не должно быть идентично названию."
            )

        return cleaned_data
