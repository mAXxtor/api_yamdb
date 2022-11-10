import re

from django.core.exceptions import ValidationError


def validate_username(username):
    """
    Запрет использования имени пользователя me.
    Regex валидация имени пользователя.
    """
    if username == 'me':
        raise ValidationError('Нельзя использовать "me" как имя пользователя')
    if re.compile(r'[\w.@+-]+').fullmatch(username) is None:
        raise ValidationError(
            'Имя пользователя должно быть не более 150 символов, и '
            'состоять из букв, цифр и символов ./@/+/-/_')
    return username
