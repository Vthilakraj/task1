import django_filters
from django.db.models import Q
from .models import Movie, Genre, Language


class MovieFilter(django_filters.FilterSet):
    # Multi-select genre filter (OR logic): ?genres=1&genres=2
    genres = django_filters.ModelMultipleChoiceFilter(
        field_name="genres",
        queryset=Genre.objects.all(),
        conjoined=False,
    )

    # Multi-select language filter: ?languages=1&languages=2
    languages = django_filters.ModelMultipleChoiceFilter(
        field_name="language",
        queryset=Language.objects.all(),
    )

    year_min = django_filters.NumberFilter(field_name="release_year", lookup_expr="gte")
    year_max = django_filters.NumberFilter(field_name="release_year", lookup_expr="lte")
    rating_min = django_filters.NumberFilter(field_name="rating", lookup_expr="gte")
    rating_max = django_filters.NumberFilter(field_name="rating", lookup_expr="lte")
    search = django_filters.CharFilter(method="filter_search")

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value)
        )

    class Meta:
        model = Movie
        fields = ["genres", "languages", "year_min", "year_max", "rating_min", "rating_max", "search"]
