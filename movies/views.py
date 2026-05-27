from django.db.models import Count, Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Movie, Genre, Language
from .serializers import (
    MovieListSerializer, MovieDetailSerializer,
    GenreSerializer, LanguageSerializer,
    GenreWithCountSerializer, LanguageWithCountSerializer,
)
from .filters import MovieFilter
from .pagination import MoviePagination


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Movie catalog with server-side multi-select filtering, pagination, and sorting.

    Filtering strategy:
    - Genre and language filters use indexed FK/M2M fields — no full-table scans.
    - filter_counts is computed in a single aggregation query per dimension,
      scoped to the currently active filters (excluding that dimension) so counts
      reflect what remains selectable, not just the global totals.
    - prefetch_related for genres prevents N+1 queries on list serialization.
    """

    serializer_class = MovieListSerializer
    pagination_class = MoviePagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MovieFilter
    ordering_fields = ["title", "release_year", "rating"]
    ordering = ["-rating"]

    def get_queryset(self):
        return (
            Movie.objects
            .select_related("language")          # avoids per-row language query
            .prefetch_related("genres")           # avoids N+1 on genres
            .only(                               # project only needed columns
                "id", "title", "release_year", "rating",
                "language", "poster_url", "description",
            )
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return MovieDetailSerializer
        return MovieListSerializer

    @action(detail=False, methods=["get"], url_path="filter-counts")
    def filter_counts(self, request):
        """
        Returns per-genre and per-language counts scoped to active filters.

        For genre counts: apply all active filters EXCEPT genres, then count
        movies per genre — so a user sees how many movies each genre would
        yield given their other active filters.

        For language counts: same principle — exclude language filter, apply
        the rest, then count per language.

        Both aggregations hit only indexed columns and emit a single GROUP BY
        query each, making this O(1) round trips regardless of catalog size.
        """
        params = request.query_params

        # Base queryset with non-genre, non-language filters applied
        base_qs = Movie.objects.all()

        year_min = params.get("year_min")
        year_max = params.get("year_max")
        rating_min = params.get("rating_min")
        rating_max = params.get("rating_max")
        search = params.get("search")

        if year_min:
            base_qs = base_qs.filter(release_year__gte=year_min)
        if year_max:
            base_qs = base_qs.filter(release_year__lte=year_max)
        if rating_min:
            base_qs = base_qs.filter(rating__gte=rating_min)
        if rating_max:
            base_qs = base_qs.filter(rating__lte=rating_max)
        if search:
            from django.db.models import Q
            base_qs = base_qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

        # Genre counts: apply language filter but not genre filter
        language_ids = params.getlist("languages")
        genre_qs = base_qs
        if language_ids:
            genre_qs = genre_qs.filter(language__in=language_ids)

        genre_counts = (
            Genre.objects
            .filter(movies__in=genre_qs)
            .annotate(count=Count("movies", distinct=True))
            .values("id", "name", "count")
            .order_by("name")
        )

        # Language counts: apply genre filter but not language filter
        genre_ids = params.getlist("genres")
        lang_qs = base_qs
        if genre_ids:
            lang_qs = lang_qs.filter(genres__in=genre_ids).distinct()

        language_counts = (
            Language.objects
            .filter(movies__in=lang_qs)
            .annotate(count=Count("movies", distinct=True))
            .values("id", "name", "code", "count")
            .order_by("name")
        )

        return Response({
            "genres": GenreWithCountSerializer(genre_counts, many=True).data,
            "languages": LanguageWithCountSerializer(language_counts, many=True).data,
        })


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = None


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    pagination_class = None
