<div id="header" align="center">
  <img src="https://media.giphy.com/media/l41lRVmlnknDV3n9u/giphy.gif" width="100"/>
</div>

## <div align="center"> Api Yamdb </div>
API для проекта YaMDb, который собирает отзывы пользователей на произведения. Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка». Список категорий может быть расширен. Произведению может быть присвоен жанр из списка предустановленных. Пользователи могут оставить к произведениям текстовые отзывы и поставить произведению оценку, из пользовательских оценок формируется усреднённая оценка произведения — рейтинг.

## Технологии
Python 3.7.9
Django 2.2.16
Django REST Framework 3.12.4

## Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/mAXxtor/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции из папки проекта:

```
cd api_yamdb
```

```
python manage.py migrate
```

Если необходимо, загрузить тестовые данные:

```
python manage.py load_test_data
```

Запустить проект:

```
python manage.py runserver
```

## Примеры запросов к API:

Получение списка всех категорий:
```
GET
http://127.0.0.1:8000/api/v1/categories/
```

Получение списка всех произведений:
```
GET
http://127.0.0.1:8000/api/v1/titles/
```

Получение списка всех отзывов к произведению:
```
GET
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/
```

Получение списка всех комментариев к отзыву:
```
GET
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/
```

### Полная документация по Api содержится в [ReDoc](http://127.0.0.1:8000/redoc/).

### Авторы
[Yandex Practicum], [Анатолий Редько], [Федор Сидоров], [Максим Вербицкий]

[//]: #

   [Yandex Practicum]: <https://practicum.yandex.ru/>
   [Анатолий Редько]: <https://github.com/krankir>
   [Федор Сидоров]: <https://github.com/FedorSidorow>
   [Максим Вербицкий]: <https://github.com/mAXxtor>
