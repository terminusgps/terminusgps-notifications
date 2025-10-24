from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase, override_settings
from terminusgps.authorizenet.constants import Environment, ValidationMode

from terminusgps_notifications import models, views


@override_settings(
    MERCHANT_AUTH_ENVIRONMENT=Environment.SANDBOX,
    MERCHANT_AUTH_VALIDATION_MODE=ValidationMode.TEST,
)
class DashboardViewTestCase(TestCase):
    def setUp(self) -> None:
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
        self.test_customer = (
            models.TerminusgpsNotificationsCustomer.objects.create(
                user=self.test_user
            )
        )
        self.factory = RequestFactory()
        self.client = Client()
        self.endpoint = "/dashboard/"
        self.view_cls = views.DashboardView

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

    def test_context(self) -> None:
        """Fails if the view context didn't have ``customer``, ``has_token`` and ``login_params``."""
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn("customer", context)


@override_settings(
    MERCHANT_AUTH_ENVIRONMENT=Environment.SANDBOX,
    MERCHANT_AUTH_VALIDATION_MODE=ValidationMode.TEST,
)
class AccountViewTestCase(TestCase):
    def setUp(self) -> None:
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
        self.test_customer = (
            models.TerminusgpsNotificationsCustomer.objects.create(
                user=self.test_user
            )
        )
        self.factory = RequestFactory()
        self.client = Client()
        self.endpoint = "/account/"
        self.view_cls = views.AccountView

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

    def test_context(self) -> None:
        """Fails if the view context didn't have ``customer``, ``has_token`` and ``login_params``."""
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn("customer", context)
        self.assertIn("has_token", context)
        self.assertIn("login_params", context)

    def test_wialon_token_creation(self) -> None:
        """Fails if a new Wialon API token wasn't created and saved for the user."""
        self.client.login(**self.test_creds)
        self.client.get(
            self.endpoint,
            query_params={
                "user_name": self.test_creds["username"],
                "access_token": "1234",
            },
        )
        self.test_customer.refresh_from_db()
        self.assertTrue(hasattr(self.test_customer, "token"))
        self.assertEqual(self.test_customer.token.name, "1234")


@override_settings(
    MERCHANT_AUTH_ENVIRONMENT=Environment.SANDBOX,
    MERCHANT_AUTH_VALIDATION_MODE=ValidationMode.TEST,
)
class SubscriptionViewTestCase(TestCase):
    def setUp(self) -> None:
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
        self.test_customer = (
            models.TerminusgpsNotificationsCustomer.objects.create(
                user=self.test_user
            )
        )
        self.factory = RequestFactory()
        self.client = Client()
        self.endpoint = "/subscription/"
        self.view_cls = views.SubscriptionView

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

    def test_context(self) -> None:
        """Fails if the view context didn't have ``customer``."""
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn("customer", context)


@override_settings(
    MERCHANT_AUTH_ENVIRONMENT=Environment.SANDBOX,
    MERCHANT_AUTH_VALIDATION_MODE=ValidationMode.TEST,
)
class NotificationsViewTestCase(TestCase):
    def setUp(self) -> None:
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
        self.test_customer = (
            models.TerminusgpsNotificationsCustomer.objects.create(
                user=self.test_user
            )
        )
        self.factory = RequestFactory()
        self.client = Client()
        self.endpoint = "/notifications/"
        self.view_cls = views.NotificationsView

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

    def test_context(self) -> None:
        """Fails if the view context didn't have ``customer`` or ``has_token``."""
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn("customer", context)
        self.assertIn("has_token", context)


@override_settings(
    MERCHANT_AUTH_ENVIRONMENT=Environment.SANDBOX,
    MERCHANT_AUTH_VALIDATION_MODE=ValidationMode.TEST,
)
class CustomerSubscriptionCreateViewTestCase(TestCase):
    def setUp(self) -> None:
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
        self.test_customer = (
            models.TerminusgpsNotificationsCustomer.objects.create(
                user=self.test_user
            )
        )
        self.factory = RequestFactory()
        self.client = Client()
        self.endpoint = "/subscriptions/create/"
        self.view_cls = views.CustomerSubscriptionCreateView

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

    def test_exclusive_form_fields(self) -> None:
        """Fails if the form fields ``payment_profile`` and ``address_profile`` contained data from other customers."""
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        form = view.get_form()
        print(f"{form.is_bound = }")
