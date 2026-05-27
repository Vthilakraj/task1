"""
Management command to seed the database with realistic movie data.
Usage: python manage.py seed_movies --count 5000
"""
import random
from django.core.management.base import BaseCommand
from django.db import transaction
from movies.models import Genre, Language, Movie

GENRES = [
    "Action", "Adventure", "Animation", "Biography", "Comedy",
    "Crime", "Documentary", "Drama", "Fantasy", "Horror",
    "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller",
    "War", "Western", "Family", "Sport", "History",
]

LANGUAGES = [
    ("English", "en"), ("Spanish", "es"), ("French", "fr"),
    ("German", "de"), ("Japanese", "ja"), ("Korean", "ko"),
    ("Hindi", "hi"), ("Mandarin", "zh"), ("Italian", "it"),
    ("Portuguese", "pt"), ("Russian", "ru"), ("Arabic", "ar"),
]

TITLE_PREFIXES = ["The", "A", "Dark", "Lost", "Last", "First", "Final", "Broken", "Silent", "Hidden"]
TITLE_MIDDLES = [
    "Shadow", "Storm", "Knight", "Dragon", "Legend", "Echo", "Flame",
    "Night", "Dawn", "Star", "River", "Mountain", "City", "Ocean",
]
TITLE_SUFFIXES = [
    "Rising", "Falls", "Returns", "Awakens", "Begins", "Ends",
    "Chronicles", "Legacy", "Origins", "Reborn",
]


def make_title(i):
    pre = random.choice(TITLE_PREFIXES)
    mid = random.choice(TITLE_MIDDLES)
    suf = random.choice(TITLE_SUFFIXES)
    return f"{pre} {mid} {suf} {i}"


class Command(BaseCommand):
    help = "Seed database with sample movie data"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=500)

    def handle(self, *args, **options):
        count = options["count"]
        self.stdout.write(f"Seeding {count} movies...")

        with transaction.atomic():
            genres = []
            for name in GENRES:
                g, _ = Genre.objects.get_or_create(name=name)
                genres.append(g)

            languages = []
            for name, code in LANGUAGES:
                lang, _ = Language.objects.get_or_create(name=name, defaults={"code": code})
                languages.append(lang)

            batch_size = 500
            movies_to_create = []
            for i in range(1, count + 1):
                movies_to_create.append(Movie(
                    title=make_title(i),
                    release_year=random.randint(1970, 2024),
                    rating=round(random.uniform(1.0, 10.0), 1),
                    language=random.choice(languages),
                    description=f"An exciting film number {i}.",
                ))
                if len(movies_to_create) >= batch_size:
                    created = Movie.objects.bulk_create(movies_to_create)
                    self._assign_genres(created, genres)
                    movies_to_create = []
                    self.stdout.write(f"  inserted {i} movies...")

            if movies_to_create:
                created = Movie.objects.bulk_create(movies_to_create)
                self._assign_genres(created, genres)

        self.stdout.write(self.style.SUCCESS(f"Done. Total movies: {Movie.objects.count()}"))

    def _assign_genres(self, movies, genres):
        through = Movie.genres.through
        pairs = []
        for movie in movies:
            picked = random.sample(genres, k=random.randint(1, 4))
            for g in picked:
                pairs.append(through(movie_id=movie.pk, genre_id=g.pk))
        through.objects.bulk_create(pairs, ignore_conflicts=True)
