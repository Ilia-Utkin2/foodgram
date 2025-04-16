from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.users_views import UserViewSet
from api.views import IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('users', UserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recips')

urlpatterns = [
    path('', include(router.urls)),
]
