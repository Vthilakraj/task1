from rest_framework import serializers
from .models import Movie, Genre, Language


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["id", "name", "code"]


class MovieListSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    language = LanguageSerializer(read_only=True)

    class Meta:
        model = Movie
        fields = ["id", "title", "release_year", "rating", "genres", "language", "poster_url"]


class MovieDetailSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    language = LanguageSerializer(read_only=True)

    class Meta:
        model = Movie
        fields = ["id", "title", "release_year", "rating", "genres", "language",
                  "description", "poster_url", "created_at"]


class GenreWithCountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    count = serializers.IntegerField()


class LanguageWithCountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    count = serializers.IntegerField()
