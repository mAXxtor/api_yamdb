from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    """Класс раздела Пользователи."""
    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name', 'bio', 'role')
    search_fields = ('username', 'email',)
    list_filter = ('role',)
    list_editable = ('role',)


admin.site.register(User, UserAdmin)
