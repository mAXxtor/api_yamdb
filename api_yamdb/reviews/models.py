from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError
# from django.contrib.auth.models import AbstractUser
import datetime as dt

from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()

# class User(AbstractUser):
#     username = models.CharField(max_length=256)
#     email = models.EmailField()
#     role = models.CharField(max_length=56)
#     bio = models.TextField(max_length=56)
#     first_name = models.CharField(max_length=56)
#     last_name = models.CharField(max_length=50)


def validate_year(value):
    if value > dt.datetime.year:
        raise ValidationError(
            f'Год не может быть больше текущего! У вас: {value}'
        )


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField()  # validators=(validate_year,)
    description = models.TextField(max_length=250, blank=True, null=True)
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        blank=True,
        related_name='titles'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )
    score = models.PositiveSmallIntegerField(
        validators=(MaxValueValidator(10), MinValueValidator(1)),
        error_messages={'validators': 'Диапазон оценки от 1 до 10!'}
    )


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(max_length=250)
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    def __str__(self):
        return self.text
