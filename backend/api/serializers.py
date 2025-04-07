from foodgram.models import AmountIngredients, Ingredient, Recipe, Tag
from rest_framework import serializers
from users.serializers import Base64ImageField, UserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = AmountIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = ingredients = RecipeIngredientSerializer(
        source='amount_ingredients',
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        extra_kwargs = {
            'author': {'read_only': True}
        }

    def get_is_favorited(self, obj):
        if self.context.get('request') is None:
            return False
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj in user.favorited.all()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request') is None:
            return False
        user = self.context['request'].user
        if user.is_authenticated:
            return obj in user.shopping_cart.all()
        return False


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        source='amount_ingredients',
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('amount_ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags_data)

        for ingredient_data in ingredients_data:
            AmountIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('amount_ingredients', None)
        tags_data = validated_data.pop('tags', None)

        instance = super().update(instance, validated_data)

        if tags_data is not None:
            instance.tags.set(tags_data)
        if ingredients_data is not None:
            instance.amount_ingredients.all().delete()
            for ingredient_data in ingredients_data:
                AmountIngredients.objects.create(
                    recipe=instance,
                    ingredient=ingredient_data['ingredient'],
                    amount=ingredient_data['amount']
                )

        return instance

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data

    def validate(self, data):
        if not data.get('amount_ingredients'):
            raise serializers.ValidationError(
                'Рецепт не может быть без ингредиентов')

        ingredients = [
            item['ingredient'].id for item in data['amount_ingredients']]
        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться')

        for item in data['amount_ingredients']:
            if item['amount'] <= 0:
                raise serializers.ValidationError(
                    'Количество должно быть больше 0')

        if not data.get('tags'):
            raise serializers.ValidationError('Рецепт не может быть без tag')
        tags = [tag.id for tag in data['tags']]
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Т не должны повторяться')

        return data
