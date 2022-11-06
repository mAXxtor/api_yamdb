from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    """
    Пользователь является супрюзером или имеет роль администратора.
    Просмотр доступен всем пользователям.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.is_admin
        return False


class IsRoleAdmin(permissions.BasePermission):
    """
    Пользователь является супрюзером или имеет роль администратора.
    """
    def has_permission(self, request, view):
        user = request.user
        return (user.is_admin or user.is_superuser)

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (user.is_admin or user.is_superuser)


# class AdminOrReadOnly(permissions.BasePermission):

#     def has_permission(self, request, view):
#         return (request.method in permissions.SAFE_METHODS
#                 or (request.user.is_authenticated
#                     and request.user.is_admin))

#     def has_object_permission(self, request, view, obj):
#         return (request.method in permissions.SAFE_METHODS
#                 or (request.user.is_authenticated
#                     and request.user.is_admin))


class IsAuthorModerAdminOrReadOnly(permissions.BasePermission):
    """
    Пользователь является супрюзером, автором или имеет роль администратора
    или модератора. Просмотр доступен всем пользователям.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
            or request.user.is_superuser
        )
