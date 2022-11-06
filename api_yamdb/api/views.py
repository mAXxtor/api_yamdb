from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Title, User

from django.conf import settings
from user.models import User
from reviews.models import Category, Review
from .email import send_confirmation_code
from .mixins import CreateDeleteListViewSet
from .serializers import (CommentSerializer, ReviewSerializer, SignUpSerializer, TokenSerializer, CategorySerializer,
                          AdminUserSerializer,)
from .permissions import IsAdmin, IsRoleAdmin
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


# class CategoryViewSet(CreateDeleteListViewSet):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = (IsAuthenticatedOrReadOnly, IsAdmin,)
#     pagination_class = LimitOffsetPagination
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('=name',)
#     def destroy(self, request, *args, **kwargs):
#         category = get_object_or_404(Category, slug=kwargs['pk'])
#         if request.user.is_admin or request.user.is_superuser:
#             self.perform_destroy(category)
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response(status=status.HTTP_403_FORBIDDEN)

#     def perform_destroy(self, category):
#         category.delete()


class ConfCodeView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        email = serializer.validated_data.get('email')
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения регистрации',
            message='Вы зарегистрировались на YAMDB!'
                    f'Ваш код подтвержения: {confirmation_code}',
            from_email=settings.ADMIN_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        username = serializer.data['username']
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.data['confirmation_code']
        if not default_token_generator.check_token(user, confirmation_code):
            return Response({'Неверный код'},
                            status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken.for_user(user)
        return Response({'token': token.access_token},
                        status=status.HTTP_200_OK)


class UserRegView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_confirmation_code(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = (IsRoleAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


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
        return Response(status=status.HTTP_202_ACCEPTED)


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
        return Response(status=status.HTTP_202_ACCEPTED)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

