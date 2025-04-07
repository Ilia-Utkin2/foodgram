from rest_framework import permissions


class UpdateOnlyAdminOrAuthor(permissions.BasePermission):
    """Разрешение на обновление только для автора или администратора."""

    def has_permission(self, request, view):
        """Проверка общего доступа."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Проверка доступа к конкретному объекту."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and (request.user.is_staff or request.user == obj.author)
        )
