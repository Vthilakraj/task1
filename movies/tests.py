from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Movie, Genre, Language


def make_data():
    en, _ = Language.objects.get_or_create(name="English", code="en")
    fr, _ = Language.objects.get_or_create(name="French", code="fr")
    action, _ = Genre.objects.get_or_create(name="Action")
    drama, _ = Genre.objects.get_or_create(name="Drama")

    m1 = Movie.objects.create(title="Alpha", release_year=2020, rating=8.5, language=en)
    m1.genres.add(action)

    m2 = Movie.objects.create(title="Beta", release_year=2018, rating=6.0, language=fr)
    m2.genres.add(drama)

    m3 = Movie.objects.create(title="Gamma", release_year=2022, rating=7.2, language=en)
    m3.genres.add(action, drama)

    return en, fr, action, drama, m1, m2, m3


class MovieListTests(APITestCase):
    def setUp(self):
        self.en, self.fr, self.action, self.drama, self.m1, self.m2, self.m3 = make_data()

    def test_list_all_movies(self):
        resp = self.client.get("/api/movies/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 3)

    def test_filter_by_single_genre(self):
        resp = self.client.get(f"/api/movies/?genres={self.action.pk}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [m["id"] for m in resp.data["results"]]
        self.assertIn(self.m1.pk, ids)
        self.assertIn(self.m3.pk, ids)
        self.assertNotIn(self.m2.pk, ids)

    def test_filter_by_multiple_genres(self):
        resp = self.client.get(f"/api/movies/?genres={self.action.pk}&genres={self.drama.pk}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # OR logic: all three movies match at least one genre
        self.assertEqual(resp.data["count"], 3)

    def test_filter_by_language(self):
        resp = self.client.get(f"/api/movies/?languages={self.en.pk}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [m["id"] for m in resp.data["results"]]
        self.assertIn(self.m1.pk, ids)
        self.assertIn(self.m3.pk, ids)
        self.assertNotIn(self.m2.pk, ids)

    def test_filter_by_genre_and_language(self):
        resp = self.client.get(f"/api/movies/?genres={self.action.pk}&languages={self.en.pk}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [m["id"] for m in resp.data["results"]]
        self.assertIn(self.m1.pk, ids)
        self.assertIn(self.m3.pk, ids)
        self.assertNotIn(self.m2.pk, ids)

    def test_sort_by_rating(self):
        resp = self.client.get("/api/movies/?ordering=rating")
        ratings = [float(m["rating"]) for m in resp.data["results"]]
        self.assertEqual(ratings, sorted(ratings))

    def test_sort_by_release_year_desc(self):
        resp = self.client.get("/api/movies/?ordering=-release_year")
        years = [m["release_year"] for m in resp.data["results"]]
        self.assertEqual(years, sorted(years, reverse=True))

    def test_rating_range_filter(self):
        resp = self.client.get("/api/movies/?rating_min=7.0")
        for m in resp.data["results"]:
            self.assertGreaterEqual(float(m["rating"]), 7.0)

    def test_year_range_filter(self):
        resp = self.client.get("/api/movies/?year_min=2019&year_max=2022")
        for m in resp.data["results"]:
            self.assertGreaterEqual(m["release_year"], 2019)
            self.assertLessEqual(m["release_year"], 2022)

    def test_pagination(self):
        resp = self.client.get("/api/movies/?page_size=2")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 2)
        self.assertEqual(resp.data["count"], 3)
        self.assertEqual(resp.data["total_pages"], 2)

    def test_filter_counts_endpoint(self):
        resp = self.client.get("/api/movies/filter-counts/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("genres", resp.data)
        self.assertIn("languages", resp.data)
        genre_names = [g["name"] for g in resp.data["genres"]]
        self.assertIn("Action", genre_names)
        self.assertIn("Drama", genre_names)

    def test_filter_counts_scoped_by_language(self):
        # When filtered to French, only Drama should appear
        resp = self.client.get(f"/api/movies/filter-counts/?languages={self.fr.pk}")
        genre_names = [g["name"] for g in resp.data["genres"]]
        self.assertIn("Drama", genre_names)
        self.assertNotIn("Action", genre_names)

    def test_movie_detail(self):
        resp = self.client.get(f"/api/movies/{self.m1.pk}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["title"], "Alpha")
        self.assertIn("description", resp.data)
