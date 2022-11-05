from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import status

from reviews.models import Genre, Title, Category
from .serializers import (
    GenreSerializer, CategorySerializer, TitleSerializer
)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=category', '=genre', '=year', '=name')


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def destroy(self, request, *args, **kwargs):
        genre_slug = kwargs['slug']
        get_object_or_404(Genre, slug=genre_slug)
        Genre.objects.filter(slug=genre_slug).delete()
        return Response(status=status.HTTP_202_ACCEPTED) # что то нужно вернуть кроме кода?


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def destroy(self, request, *args, **kwargs):
        category_slug = kwargs['slug']
        get_object_or_404(Category, slug=category_slug)
        Genre.objects.filter(slug=category_slug).delete()
        return Response(status=status.HTTP_202_ACCEPTED) # что то нужно вернуть кроме кода?
