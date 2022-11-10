from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year


class GenreCategoryAbstractModel(models.Model):
    """Абстрактная модель для Жанра и Категории."""
    name = models.CharField('Наименование', max_length=settings.LIMIT_NAME)
    slug = models.SlugField(
        'Slug', unique=True, max_length=settings.LIMIT_SLUG, db_index=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(GenreCategoryAbstractModel):
    """Жанр произведения."""
    class Meta(GenreCategoryAbstractModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        default_related_name = "genres"


class Category(GenreCategoryAbstractModel):
    """Категория произведения."""
    class Meta(GenreCategoryAbstractModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        default_related_name = "categories"


class Title(models.Model):
    """Произведение."""
    name = models.CharField(
        'Название произведения',
        max_length=settings.LIMIT_NAME)
    year = models.PositiveSmallIntegerField(
        'Год создания произведения',
        validators=(MinValueValidator(0), validate_year,),
        db_index=True
    )
    description = models.TextField(
        'Описание произведения', blank=True,)
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        blank=True,
        related_name='titles',
        verbose_name='Жанр произведения'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
        verbose_name='Категория произведения'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Промежуточная модель соеднинения Жанров и Произведений."""
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} {self.genre}'


class ReviewCommentsAbstractModel(models.Model):
    """Абстрактная модель для Отзыва и Комментария."""
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='username пользователя'
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True,)

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[settings.LIMIT_TEXT]


class Review(ReviewCommentsAbstractModel):
    """Отзыв на произведение."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=(MaxValueValidator(10), MinValueValidator(1)),
        error_messages={'validators': 'Диапазон оценки от 1 до 10!'},
        default=1
    )

    class Meta(ReviewCommentsAbstractModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review'
            )
        ]


class Comment(ReviewCommentsAbstractModel):
    """Комментарии к отзывам."""
    review = models.ForeignKey(
        to=Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )

    class Meta(ReviewCommentsAbstractModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = "comments"
