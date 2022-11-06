from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    """
    Пользователь имеет роль администратора.
    Просмотр доступен всем пользователям.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsRoleAdmin(permissions.BasePermission):
    """
    Только роль администратора.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorModerAdminOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Пользователь является супрюзером, автором или имеет роль администратора
    или модератора. Просмотр доступен всем пользователям.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
        )
