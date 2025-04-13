from django_filters import rest_framework as filters

from foodgram.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        label='Filter by tag slugs'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']
