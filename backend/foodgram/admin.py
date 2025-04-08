from django.contrib import admin

from .models import Ingredient, Recipe, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_count')
    list_select_related = ('author',)
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)  # Фильтрация по тегам
    inlines = [RecipeIngredientInline]
    filter_horizontal = ('tags',)  # Для удобного выбора тегов

    def favorite_count(self, obj):
        return obj.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)  # Поиск по названию
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
