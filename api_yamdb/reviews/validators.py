import datetime as dt

from django.core.exceptions import ValidationError


def validate_year(value):
    if value > dt.date.today().year:
        raise ValidationError(
            f'Год не может быть больше текущего! У вас: {value}'
        )
    return value
