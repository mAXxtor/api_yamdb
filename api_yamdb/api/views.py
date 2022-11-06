from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFilter
from .email import send_confirmation_code
from .permissions import (IsAuthorModerAdminOrReadOnly, AdminOrReadOnly,
                          IsRoleAdmin)
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    NotAdminUserSerializer, ReviewSerializer, SignUpSerializer,
    TitleSerializer, TokenSerializer, UserSerializer
)
from reviews.models import Category, Genre, Review, Title
from users.models import User


class ConfCodeView(APIView):
    """Отправляет пользователю код подтверждения."""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        email = serializer.validated_data.get('email')  # type: ignore
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения регистрации',
            message='Вы зарегистрировались на YAMDB!'
                    f'Ваш код подтвержения: {confirmation_code}',
            from_email=settings.ADMIN_EMAIL,
            recipient_list=[email],  # type: ignore
            fail_silently=False,
        )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenView(APIView):
    """Проверяет код подтверждения и отправляет токен."""
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
    """Регистрирует пользователя."""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_confirmation_code(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    """Получает список пользователей. Доступен адмиристратору."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsRoleAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me')
    def get_current_user_info(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = UserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            else:
                serializer = NotAdminUserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)


class TitleViewSet(viewsets.ModelViewSet):
    """Класс произведения. Доступен администратору."""
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).all()
    serializer_class = TitleSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    ordering_fields = ('name',)


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """Класс жанра произведения. Доступен администратору."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def destroy(self, request, *args, **kwargs):
        genre_slug = kwargs['slug']
        get_object_or_404(Genre, slug=genre_slug)
        Genre.objects.filter(slug=genre_slug).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Класс категории произведения. Доступен администратору."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def destroy(self, request, *args, **kwargs):
        category_slug = kwargs['slug']
        get_object_or_404(Category, slug=category_slug)
        Category.objects.filter(slug=category_slug).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(viewsets.ModelViewSet):
    """Просмотр и редактирование рецензий."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorModerAdminOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()  # type: ignore

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Просмотр и редактирование комментариев."""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorModerAdminOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()  # type: ignore

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
