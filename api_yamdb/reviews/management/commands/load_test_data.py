from csv import DictReader

from django.conf import settings
from django.core.management import BaseCommand

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import User

TABLES = {
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    GenreTitle: 'genre_title.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
    User: 'users.csv',
}


# class Command(BaseCommand):

#     def handle(self, *args, **kwargs):
#         for model, csv_file in TABLES.items():
#             with open(
#                 f'{settings.BASE_DIR}/static/data/{csv_file}',
#                 'r',
#                 encoding='utf-8'
#             ) as csv_f:
#                 model.objects.bulk_create(
#                     model(**data) for data in DictReader(csv_f))
#             self.stdout.write(self.style.SUCCESS(f'Загружено {csv_file}'))
#         self.stdout.write(self.style.SUCCESS('Все данные загружены'))
class Command(BaseCommand):
    help = 'Filling tables using csv file from static/data.'

    def handle(self, *args, **options):
        for model in MODELS:
            try:
                csv_path = os.path.join(
                    ABS_PATH,
                    f'static/data/{MODELS.get(model)}'
                )
                with open(csv_path, encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        model.objects.get_or_create(
                            **dict(row)
                        )

            except IntegrityError as _ex:
                print(f'Cant upload data: {_ex.args}')
            except TypeError as _ex:
                print(f'Cant find column name to upload data {_ex.args}')
            except ValueError as _ex:
                print(f'Wrong type data: {_ex.args}')
            else:
                print(f'{MODELS.get(model)} file was correct upload')
