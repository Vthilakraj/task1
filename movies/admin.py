from django.contrib import admin
from .models import Movie, Genre, Language


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "code"]
    search_fields = ["name", "code"]


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "release_year", "rating", "language"]
    list_filter = ["genres", "language", "release_year"]
    search_fields = ["title"]
    filter_horizontal = ["genres"]
    raw_id_fields = ["language"]
