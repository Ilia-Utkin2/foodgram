from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.models import (AmountIngredients, Favorited, Ingredient, Recipe,
                             ShoppingCart, Tag)
from reportlab.pdfbase import pdfmetrics
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.serializers import SubscribRiciptesSerializer

from .pagination import RecipPagination
from .permissions import UpdateOnlyAdminOrAuthor
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeSerializer, TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [UpdateOnlyAdminOrAuthor]
    pagination_class = RecipPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags')

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if user.favorited.filter(pk=recipe.pk).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorited.objects.create(user=user, recipe=recipe)
            serializer = SubscribRiciptesSerializer(recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED
                            )

        favorited = Favorited.objects.filter(
            user=user, recipe=recipe).first()

        if not favorited:
            return Response(
                {'errors': 'Рецепта нет в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorited.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='shopping_cart'
            )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if user.shopping_cart.filter(pk=recipe.pk).exists():
                return Response(
                    {'errors': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = SubscribRiciptesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        shopping_cart = ShoppingCart.objects.get(user=user, recipe=recipe)

        if not shopping_cart:
            return Response(
                {'errors': 'Рецепта нет в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'],
            url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return Response(
            {"short-link": recipe.get_short_url()},
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        user = request.user
        try:
            recipe_ids = user.shopping_cart.all().values_list('recipe_id', flat=True)
            if not recipe_ids:
                return Response(
                    {'detail': 'Ваша корзина покупок пуста'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'detail': f'Ошибка при получении корзины: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            ingredients = (
                AmountIngredients.objects
                .filter(recipe_id__in=recipe_ids)
                .values(
                    'ingredient__name',
                    'ingredient__measurement_unit'
                )
                .annotate(total_amount=Sum('amount'))
                .order_by('ingredient__name')
            )
            print([(i['ingredient__name'], i['total_amount'],
                  i['ingredient__measurement_unit']) for i in ingredients])
            print(pdfmetrics.getRegisteredFontNames())
        except Exception as e:
            return Response(
                {'detail': f'Ошибка при получении ингредиентов: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        text_content = "\n".join([
            f"{item['ingredient__name']} - {item['total_amount']} {item['ingredient__measurement_unit']}"
            for item in ingredients
        ])
        response = HttpResponse(
            text_content, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response
