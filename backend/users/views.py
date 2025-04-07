from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from foodgram.models import Subscriptions
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.paginations import UsersPagination
from users.permissions import UpdateOnlyAdmin
from users.serializers import (AvatarSerializer, SubscribeSerializer,
                               UserSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Представление для управления пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UpdateOnlyAdmin]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = UsersPagination

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['get', 'put', 'delete'],  # Используем PUT вместо PATCH
        url_path='me/avatar',
        permission_classes=[permissions.IsAuthenticated]
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'GET':
            return Response({
                'avatar': user.avatar.url if user.avatar else None
            })

        elif request.method == 'PUT':
            # PUT требует полной замены ресурса
            if 'avatar' not in request.data:
                return Response(
                    {'error': 'avatar field is required for PUT'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = AvatarSerializer(
                user,
                data=request.data
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == 'DELETE':
            user.avatar = None
            user.save()

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['post'],  # Используем PUT вместо PATCH
        url_path='set_password',
        permission_classes=[permissions.IsAuthenticated]
    )
    def set_password(self, request):
        user = request.user
        if 'new_password' not in request.data:
            return Response(
                {'error': 'new_password field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'current_password' not in request.data:
            return Response(
                {'error': 'current_password field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(request.data['current_password']):
            return Response(
                {'error': 'incorrect current_password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(request.data.get('new_password'))
        user.save()
        return Response(
            {'message': 'Пароль успешно изменен'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=SubscribeSerializer
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            # Проверка существования подписки
            if Subscriptions.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                Subscriptions.objects.create(user=user, author=author)
            except IntegrityError:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE обработка
        subscription = Subscriptions.objects.filter(
            user=user, author=author).first()
        if not subscription:
            return Response(
                {'errors': 'Подписка не найдена'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        permission_classes=[permissions.IsAuthenticated],
        pagination_class=UsersPagination,
        serializer_class=SubscribeSerializer
    )
    def subscriptions(self, request):
        subscribed_authors = User.objects.filter(
            following__user=request.user
        )
        serializer_context = {'request': request}
        page = self.paginate_queryset(subscribed_authors)
        serializer = self.get_serializer(
            page,
            many=True,
            context=serializer_context
        )
        return self.get_paginated_response(serializer.data)

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method 'PUT' not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
