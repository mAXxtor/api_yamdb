from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet
from .permissions import (IsAuthorModerAdminOrReadOnly, AdminOrReadOnly,
                          IsRoleAdmin)
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    NotAdminUserSerializer, ReviewSerializer, SignUpSerializer,
    TitlePostSerialzier, TitleSerializer, TokenSerializer, UserSerializer
)
from reviews.models import Category, Genre, Review, Title
from users.models import User


class ConfCodeView(APIView):
    """Регистрация пользователя и отправка кода подтверждения."""
    USERNAME_ERROR = 'Пользователь с таким username уже существует'
    EMAIL_ERROR = 'Пользователь с таким email уже существует'

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        try:
            user, _ = User.objects.get_or_create(username=username,
                                                 email=email)
        except IntegrityError:
            message = (self.EMAIL_ERROR if
                       User.objects.filter(email=email).exists() else
                       self.USERNAME_ERROR)
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения регистрации',
            message='Вы зарегистрировались на YAMDB!'
                    f'Ваш код подтвержения: {confirmation_code}',
            from_email=settings.ADMIN_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    """Проверка кода подтверждения и отправка токена."""
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.validated_data.get('confirmation_code')
        if not default_token_generator.check_token(user, confirmation_code):
            return Response(
                {'Вы использовали неверный код подтверждения.'},
                status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken.for_user(user)
        return Response({'token': str(token.access_token)},
                        status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    """Получение списка пользователей и редактирование."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsRoleAdmin,)
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me',
        url_name='current_user_info')
    def get_current_user_info(self, request,):
        """Просмотр и редактирование своего аккаунта."""
        if request.method == 'GET':
            serializer = NotAdminUserSerializer(self.request.user)
        else:
            serializer = NotAdminUserSerializer(
                self.request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    """Класс произведения. Доступен администратору."""
    queryset = Title.objects.select_related(
        'category').prefetch_related('genre').annotate(
            rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilter
    filterset_fields = ('name',)
    ordering_fields = ('name',)

    def get_serializer_class(self):
        """
        При POST, PATCH, PUT запросах использует специальный сериализатор.
        """
        if self.request.method in ['POST', 'PATCH', 'PUT']:
            return TitlePostSerialzier
        return TitleSerializer


class GenreViewSet(CreateListDestroyViewSet):
    """Класс жанра произведения. Доступен администратору."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CreateListDestroyViewSet):
    """Класс категории произведения. Доступен администратору."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Просмотр и редактирование рецензий."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModerAdminOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Просмотр и редактирование комментариев."""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModerAdminOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
