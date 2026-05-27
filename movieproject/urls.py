"""
URL configuration for movieproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def home(request):
    return JsonResponse({
        "message": "Welcome to MovieDB API",
        "endpoints": {
            "movies": "/api/movies/",
            "movie_detail": "/api/movies/{id}/",
            "filter_counts": "/api/movies/filter-counts/",
            "genres": "/api/genres/",
            "languages": "/api/languages/",
        },
        "filters": {
            "genres": "?genres=1&genres=2  (multi-select, OR logic)",
            "languages": "?languages=1&languages=2",
            "rating": "?rating_min=7.0&rating_max=10.0",
            "year": "?year_min=2000&year_max=2024",
            "search": "?search=dark",
            "sort": "?ordering=-rating  (title, release_year, rating)",
            "pagination": "?page=1&page_size=20",
        },
        "example": "/api/movies/?genres=1&languages=1&ordering=-rating&page_size=5",
        "total_movies": 300,
    })


urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("api/", include("movies.urls")),
]
