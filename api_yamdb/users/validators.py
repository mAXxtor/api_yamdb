from rest_framework.serializers import ValidationError


def username_validation(username):
    """Запрет использования имени пользователя me."""
    if username == 'me':
        raise ValidationError('Нельзя использовать "me" как имя пользователя')
    return username
