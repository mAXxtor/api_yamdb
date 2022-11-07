from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import username_validation


ADMIN = 'admin'
MODERATOR = 'moderator'
USER = 'user'

USER_ROLE = (
    (USER, 'user'),
    (MODERATOR, 'moderator'),
    (ADMIN, 'admin'),
)


class User(AbstractUser):
    username = models.CharField(max_length=100,
                                verbose_name='Логин',
                                help_text='Укажите логин',
                                unique=True,
                                blank=False,
                                null=False,
                                validators=(username_validation,),)
    email = models.EmailField(max_length=254,
                              verbose_name='Email',
                              help_text='Укажите email',
                              unique=True,
                              blank=False,
                              null=False)
    confirmation_code = models.CharField(max_length=40,
                                         blank=True,
                                         verbose_name='Проверочный код')
    first_name = models.CharField(max_length=100,
                                  verbose_name='Имя',
                                  help_text='Укажите Имя',
                                  blank=True)
    last_name = models.CharField(max_length=100,
                                 verbose_name='Фамилия',
                                 help_text='Укажите Фамилию',
                                 blank=True)
    bio = models.TextField(max_length=1000,
                           verbose_name='Биография',
                           help_text='Укажите Биографию',
                           blank=True,)
    role = models.CharField(max_length=100,
                            verbose_name='Роль',
                            choices=USER_ROLE,
                            default=USER,
                            help_text='Роль пользователя')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(username='me'), name='username_not_me')
        ]

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.is_staff or self.role == ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR
