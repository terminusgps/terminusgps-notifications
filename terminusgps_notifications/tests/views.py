from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from terminusgps_notifications import views


class DashboardViewTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.endpoint = "/dashboard/"
        self.view_cls = views.DashboardView
        self.test_view = self.view_cls()
        self.test_creds = {
            "username": "testuser@testdomain.com",
            "email": "testuser@testdomain.com",
            "password": "super_secure_password1!",
        }
        self.test_user = get_user_model().objects.create_user(
            username=self.test_creds["username"],
            email=self.test_creds["email"],
            password=self.test_creds["password"],
        )

    def tearDown(self) -> None:
        self.test_user.delete()

    def test_anonymous_user_forbidden(self) -> None:
        """Fails if an anonymous user was able to get a 200 response from the view."""
        self.assertRedirects(
            self.client.get(self.endpoint, follow=False),
            f"/login/?next={self.endpoint}",
            fetch_redirect_response=False,
            status_code=302,
        )

    def test_authenticated_user_permitted(self) -> None:
        """Fails if an authenticated user didn't get a 200 response from the view."""
        self.client.login(**self.test_creds)
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 200)


class AccountViewTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.endpoint = "/account/"
        self.view_cls = views.AccountView
        self.test_view = self.view_cls()
        self.test_creds = {
            "username": "testuser@testdomain.com",
            "email": "testuser@testdomain.com",
            "password": "super_secure_password1!",
        }
        self.test_user = get_user_model().objects.create_user(
            username=self.test_creds["username"],
            email=self.test_creds["email"],
            password=self.test_creds["password"],
        )

    def tearDown(self) -> None:
        self.test_user.delete()

    def test_anonymous_user_forbidden(self) -> None:
        """Fails if an anonymous user was able to get a 200 response from the view."""
        self.assertRedirects(
            self.client.get(self.endpoint, follow=False),
            f"/login/?next={self.endpoint}",
            fetch_redirect_response=False,
            status_code=302,
        )

    def test_authenticated_user_permitted(self) -> None:
        """Fails if an authenticated user didn't get a 200 response from the view."""
        self.client.login(**self.test_creds)
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 200)
