from rest_framework.serializers import ValidationError


def username_validation(value):
    """Запрет использования имени пользователя me."""
    if value == 'me':
        raise ValidationError('Нельзя использовать "me" как имя пользователя')
    return value
