from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    code = models.CharField(max_length=10, unique=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=500, db_index=True)
    release_year = models.PositiveSmallIntegerField(db_index=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, db_index=True)
    genres = models.ManyToManyField(Genre, related_name="movies")
    language = models.ForeignKey(
        Language, on_delete=models.SET_NULL, null=True, related_name="movies", db_index=True
    )
    description = models.TextField(blank=True)
    poster_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-rating", "title"]
        indexes = [
            models.Index(fields=["language", "rating"], name="idx_language_rating"),
            models.Index(fields=["release_year", "rating"], name="idx_year_rating"),
            models.Index(fields=["language", "release_year"], name="idx_language_year"),
        ]

    def __str__(self):
        return f"{self.title} ({self.release_year})"
