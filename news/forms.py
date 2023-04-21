from django import forms
from django.core.exceptions import ValidationError
from django_filters import ModelMultipleChoiceFilter

from .models import Post, Category


class PostForm(forms.ModelForm):
    text = forms.CharField(min_length=20)
    category = ModelMultipleChoiceFilter(
        field_name="post_category",
        queryset=Category.objects.all(),
        label="Category",
    )

    class Meta:
        model = Post
        fields = [
            'author',
            'post_rating',
            'heading',
            'text',
            'post_category',
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
