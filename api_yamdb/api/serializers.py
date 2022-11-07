from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User
from users.validators import username_validation


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для аутентификации."""
    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate_username(self, username):
        """Валидация имени пользователя."""
        return username_validation(username)


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор для токена."""
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate_username(self, username):
        """Валидация имени пользователя."""
        return username_validation(username)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'role')

    def validate_username(self, username):
        """Валидация имени пользователя."""
        if (
            self.context['request'].method == 'POST'
            and User.objects.filter(username=username).exists()
        ):
            raise ValidationError(
                'Пользователь с таким именем уже существует.'
            )
        return username_validation(username)

    def validate_email(self, email):
        """Валидация почты пользователя."""
        if (
            self.context['request'].method == 'POST'
            and User.objects.filter(email=email).exists()
        ):
            raise ValidationError(
                'Пользователь с таким Email уже существует.'
            )
        return username_validation(email)


class NotAdminUserSerializer(UserSerializer):
    """Сериализатор для пользователя."""
    role = serializers.CharField(read_only=True)


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
            raise ValidationError(
                'Вы уже оставили отзыв к этому произведению!')
        return data

    class Meta:
        fields = '__all__'
        model = Review


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
