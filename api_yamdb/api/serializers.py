from rest_framework import serializers

from reviews.models import Genre, Title, Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Category


class TitleSerializer(serializers.ModelSerializer):

    genre = serializers.SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug'
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        model = Title
        read_only_field = ('description',)

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res['category'] = CategorySerializer(instance.category).data
        res['genre'] = []
        for genre in instance.genre.all():
            res['genre'].append(GenreSerializer(genre).data)
        return res
