from django_filters import rest_framework as filters

from foodgram.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        label='Filter by tag slugs'
    )

    is_favorited = filters.NumberFilter(
        method='filter_is_favorited',
        label='Filter favorited recipes (1/0)'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        print('adsadad')
        if value == 1 and user.is_authenticated:
            return queryset.favorited_by.all()
        return queryset
