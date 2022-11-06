from csv import DictReader

from django.conf import settings
from django.core.management import BaseCommand

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import User

TABLES = {
    Category: 'category.csv',
    Comment: 'comments.csv',
    Genre: 'genre.csv',
    GenreTitle: 'genre_title.csv',
    Review: 'review.csv',
    Title: 'titles.csv',
    User: 'users.csv',
}


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for model, csv_file in TABLES.items():
            with open(
                f'{settings.BASE_DIR}/static/data/{csv_file}',
                'r',
                encoding='utf-8'
            ) as csv_f:
                model.objects.bulk_create(
                    model(**data) for data in DictReader(csv_f))
        self.stdout.write(self.style.SUCCESS('Все данные загружены'))