import re

from django.core.exceptions import ValidationError
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.serializers import BaseSerializer

from .permissions import AdminOrReadOnly


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """Вьюсет для POST, GET и DELETE запросов.
    Поддерживает url с динамической переменной slug.
    """

    permission_classes = (AdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class UsernameSerializer(BaseSerializer):
    """Сериализатор для username."""
    def validate_username(self, username):
        if username == 'me':
            raise ValidationError(
                'Нельзя использовать "me" как имя пользователя')
        if not re.match('^[\\w.@+-]+', username):
            raise ValidationError(
                'Имя пользователя должно быть не более 150 символов, и '
                'состоять из букв, цифр и символов ./@/+/-/_')
        return username
