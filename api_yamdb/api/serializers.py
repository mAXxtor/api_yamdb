from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .mixins import UsernameSerializer
from reviews.models import Category, Comment, Genre, Review, Title
from reviews.validators import validate_year
from users.models import User


class SignUpSerializer(serializers.Serializer, UsernameSerializer):
    """Сериализатор для аутентификации."""
    username = serializers.CharField(
        max_length=settings.LIMIT_USERNAME,
        validators=[UniqueValidator(queryset=User.objects.all()), ],
        required=True)
    email = serializers.EmailField(
        max_length=settings.LIMIT_EMAIL,
        validators=[UniqueValidator(queryset=User.objects.all()), ],
        required=True)


class TokenSerializer(serializers.Serializer, UsernameSerializer):
    """Сериализатор для токена."""
    username = serializers.CharField(
        max_length=settings.LIMIT_USERNAME,
        validators=[UniqueValidator(queryset=User.objects.all()), ],
        required=True)
    confirmation_code = serializers.CharField(
        max_length=settings.LIMIT_CONF_CODE,
        required=True)


class UserSerializer(serializers.ModelSerializer, UsernameSerializer):
    """Сериализатор для пользователя."""
    username = serializers.CharField(
        max_length=settings.LIMIT_USERNAME,
        validators=[UniqueValidator(queryset=User.objects.all()), ],
        required=True)
    email = serializers.EmailField(
        max_length=settings.LIMIT_EMAIL,
        validators=[UniqueValidator(queryset=User.objects.all()), ],
        required=True)

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'role')


class NotAdminUserSerializer(UserSerializer, UsernameSerializer):
    """Сериализатор для пользователя."""
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра."""
    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории."""
    class Meta:
        fields = ('name', 'slug')
        model = Category


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведения."""
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(default=1)
    year = serializers.IntegerField(validators=[MinValueValidator(0),
                                                validate_year, ])

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category')
        model = Title
        read_only_fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category')


class TitlePostSerialzier(serializers.ModelSerializer):
    """Сериализатор для POST, PATCH, PUT произведения."""
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category')

    def to_representation(self, instance):
        return TitleSerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзыва и оценки."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    score = serializers.IntegerField(validators=[
        MinValueValidator(limit_value=1,
                          message='Минимальный рейтинг : 1'),
        MaxValueValidator(limit_value=10,
                          message='Максимальный рейтинг : 10')
    ])

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        """Валидация для отзыва."""
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        if request.method == 'POST' and Review.objects.filter(
                title=get_object_or_404(Title, id=title_id),
                author=request.user).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв к этому произведению!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментария."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'pub_date', 'author', 'review')
        model = Comment
        read_only_fields = ('review',)
