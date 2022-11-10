from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


class GenreTitleInline(admin.TabularInline):
    model = Title.genre.through


class TitleAdmin(admin.ModelAdmin):
    """Класс раздела произведений."""
    list_display = ('name', 'year', 'description', 'category', 'get_genre',)
    search_fields = ('name',)
    list_filter = ('year', 'category',)
    inlines = [GenreTitleInline]

    def get_genre(self, object):
        """Получение перечня жанров произведения."""
        return '\n'.join((genre.name for genre in object.genre.all()))

    get_genre.short_description = 'Жанры произведения'


class CategoryAdmin(admin.ModelAdmin):
    """Класс раздела категорий."""
    list_display = ('name', 'slug',)
    search_fields = ('name',)


class GenreAdmin(admin.ModelAdmin):
    """Класс раздела жанров."""
    list_display = ('name', 'slug',)
    search_fields = ('name',)


class ReviewAdmin(admin.ModelAdmin):
    """Класс раздела отзывов."""
    list_display = ('pk', 'text', 'score', 'author', 'title', 'pub_date',)
    search_fields = ('text', 'author',)
    list_filter = ('pub_date', 'author', 'title', 'score',)


class CommentAdmin(admin.ModelAdmin):
    """Класс раздела комментариев."""
    list_display = ('pk', 'text', 'review', 'author', 'pub_date',)
    search_fields = ('text', 'author',)
    list_filter = ('pub_date', 'author',)


admin.site.register(Title, TitleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
