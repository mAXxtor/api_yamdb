from collections import OrderedDict

from csv import DictReader

from django.conf import settings
from django.core.management import BaseCommand

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import User

TABLES = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    GenreTitle: 'genre_title.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):
    """Импорт тестовых данных из csv-файлов."""

    def handle(self, *args, **options):
        for model, csv_file in TABLES.items():
            self.stdout.write(f'Импорт данных из файла {csv_file}')
            with open(f'{settings.BASE_DIR}/static/data/{csv_file}',
                      encoding='utf-8') as file:
                counter = 0
                for row in DictReader(file):
                    if not model.objects.filter(id=row['id']).exists():
                        correct_row = []
                        for key, value in row.items():
                            if key == 'category':
                                continue
                                correct_row.append(
                                    (key,
                                     Category.objects.filter(id=value).first()
                                     )
                                )
                            if key == 'author':
                                correct_row.append((
                                    key,
                                    User.objects.filter(id=value).first()
                                ))
                            else:
                                correct_row.append((key, value))
                        model.objects.get_or_create(**OrderedDict(correct_row))
                        counter += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'- загружено {counter} записей'))
