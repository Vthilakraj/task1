from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MovieViewSet, GenreViewSet, LanguageViewSet

router = DefaultRouter()
router.register(r"movies", MovieViewSet, basename="movie")
router.register(r"genres", GenreViewSet, basename="genre")
router.register(r"languages", LanguageViewSet, basename="language")

urlpatterns = [
    path("", include(router.urls)),
]
