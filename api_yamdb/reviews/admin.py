from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


class GenreTitleInline(admin.TabularInline):
    model = Title.genre.through


class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'description', 'category',)
    search_fields = ('name',)
    list_filter = ('id', 'year',)
    inlines = [GenreTitleInline]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name',)
    list_filter = ('id',)


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name',)
    list_filter = ('id',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'score', 'author', 'title', 'pub_date',)
    search_fields = ('text', 'author',)
    list_filter = ('pub_date', 'author', 'title', 'score',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'review', 'author', 'pub_date',)
    search_fields = ('text', 'author',)
    list_filter = ('pub_date', 'author',)


admin.site.register(Title, TitleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
