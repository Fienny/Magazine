from django_filters import FilterSet, DateFromToRangeFilter, ChoiceFilter
from django_filters.widgets import RangeWidget

from .models import Post, Author, User


class PostFilter(FilterSet):
    published_date = DateFromToRangeFilter(widget=RangeWidget(attrs={'placeholder': 'YYYY-MM-DD'}))

    class Meta:
        model = Post

        fields = {
            'heading': ['icontains'],
            'author': ['exact'],
        }
