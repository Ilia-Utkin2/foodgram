import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from constants import MAX_EMAIL, MAX_USERNAME
from foodgram.models import Recipe

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

    def to_representation(self, value):
        if value:
            return value.url
        return None


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для редактирования администратором."""

    email = serializers.EmailField(
        max_length=MAX_EMAIL,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        max_length=MAX_USERNAME,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message='Username может содержать только буквы, цифры, '
                    'и символы @/./+/-/_',
            code='invalid_username'
        ), UniqueValidator(queryset=User.objects.all())
        ]
    )
    password = serializers.CharField(write_only=True)

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'avatar', 'password')
        read_only_fields = ('avatar', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        user = request.user
        if user in obj.follower.all():
            return True
        return False

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
        extra_kwargs = {
            'avatar': {
                'required': True,
                'allow_null': False
            }
        }

    def update(self, instance, validated_data):
        # PUT требует полного обновления, поэтому просто заменяем аватар
        instance.avatar = validated_data['avatar']
        instance.save()
        return instance


class SubscribRiciptesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if request is None:
            return False
        user = request.user
        if user in obj.follower.all():
            return True
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = obj.recipes.all()

        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                queryset = queryset[:recipes_limit]
            except ValueError:
                pass
        return SubscribRiciptesSerializer(queryset, many=True).data
