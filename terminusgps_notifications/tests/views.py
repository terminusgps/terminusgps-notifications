import os

from authorizenet import apicontractsv1
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase, override_settings
from terminusgps.authorizenet.constants import Environment, ValidationMode
from terminusgps_payments.models import AddressProfile, PaymentProfile
from terminusgps_payments.services import AuthorizenetService

from terminusgps_notifications import models, views

# TODO: Increase test coverage


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

    def test_htmx_renders_partial_template(self) -> None:
        """Fails if an HTMX request renders the main template instead of the partial template."""
        request = self.factory.get(
            self.endpoint, headers={"HX-Request": True, "HX-Boosted": False}
        )
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        view.render_to_response(view.get_context_data())
        self.assertIn("/partials/_", view.template_name)

    def test_get_context_data(self) -> None:
        """Fails if the view context didn't have ``customer`` and ``title``."""
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn("title", context)
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

    def test_htmx_renders_partial_template(self) -> None:
        """Fails if an HTMX request renders the main template instead of the partial template."""
        request = self.factory.get(
            self.endpoint, headers={"HX-Request": True, "HX-Boosted": False}
        )
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        view.render_to_response(view.get_context_data())
        self.assertIn("/partials/_", view.template_name)

    def test_get(self) -> None:
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

    def test_get_context_data(self) -> None:
        """Fails if the view context didn't have ``title``, ``customer``, ``has_token`` and ``login_params``."""
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn("title", context)
        self.assertIn("customer", context)
        self.assertIn("has_token", context)
        self.assertIn("login_params", context)


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

    def test_htmx_renders_partial_template(self) -> None:
        """Fails if an HTMX request renders the main template instead of the partial template."""
        request = self.factory.get(
            self.endpoint, headers={"HX-Request": True, "HX-Boosted": False}
        )
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        view.render_to_response(view.get_context_data())
        self.assertIn("/partials/_", view.template_name)

    def test_get_context_data(self) -> None:
        """Fails if the view context didn't have ``title`` and ``customer``."""
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn("title", context)
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

    def test_htmx_renders_partial_template(self) -> None:
        """Fails if an HTMX request renders the main template instead of the partial template."""
        request = self.factory.get(
            self.endpoint, headers={"HX-Request": True, "HX-Boosted": False}
        )
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        view.render_to_response(view.get_context_data())
        self.assertIn("/partials/_", view.template_name)

    def test_get_context_data(self) -> None:
        """Fails if the view context didn't have ``title``, ``customer`` and ``has_token``."""
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn("title", context)
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

        self.test_address = apicontractsv1.customerAddressType()
        self.test_address.firstName = "Test"
        self.test_address.lastName = "User"
        self.test_address.address = "123 Main St"
        self.test_address.city = "Houston"
        self.test_address.state = "Texas"
        self.test_address.country = "USA"
        self.test_address.zip = "77433"

        self.test_credit_card = apicontractsv1.creditCardType()
        self.test_credit_card.cardNumber = "4111111111111111"
        self.test_credit_card.expirationDate = "2029-04"
        self.test_credit_card.cardCode = "444"

        self.test_customer_profile = getattr(
            self.test_user, "customer_profile"
        )

        self.service = AuthorizenetService()
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

    def test_setup(self) -> None:
        """Fails if :py:attr:`anet_service` wasn't added to the view after calling :py:meth:`setup`."""
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        self.assertTrue(hasattr(view, "anet_service"))

    def test_get_context_data(self) -> None:
        """Fails if the view context didn't have ``title``, ``customer`` and ``form``."""
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn("title", context)
        self.assertIn("customer", context)
        self.assertIn("form", context)

    def test_get_form(self) -> None:
        """Fails if the form fields ``payment_profile`` and ``address_profile`` contained data from other customers."""
        # Create an address profile
        address_profile = AddressProfile(
            customer_profile=self.test_customer_profile
        )
        address_response = self.service.create_address_profile(
            address_profile=address_profile,
            address=self.test_address,
            default=True,
        )
        address_profile.pk = int(address_response.customerAddressId)
        address_profile.save()

        # Create a payment profile
        payment_profile = PaymentProfile(
            customer_profile=self.test_customer_profile
        )
        payment_response = self.service.create_payment_profile(
            payment_profile=payment_profile,
            address=self.test_address,
            credit_card=self.test_credit_card,
            default=True,
        )
        payment_profile.pk = int(payment_response.customerPaymentProfileId)
        payment_profile.save()

        # Initialize the form
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        form = view.get_form()

        # Evaluate form querysets
        self.assertTrue(
            not form.fields["payment_profile"]
            .queryset.difference(
                PaymentProfile.objects.for_user(self.test_user)
            )
            .exists()
        )
        self.assertTrue(
            not form.fields["address_profile"]
            .queryset.difference(
                AddressProfile.objects.for_user(self.test_user)
            )
            .exists()
        )

    def test_form_valid(self) -> None:
        """Fails if :py:meth:`form_valid` is executed without creating a subscription for the customer."""
        # TODO
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)


class CustomerStatsViewTestCase(TestCase):
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
        self.endpoint = "/stats/"
        self.view_cls = views.CustomerStatsView

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

    def test_htmx_renders_partial_template(self) -> None:
        """Fails if an HTMX request renders the main template instead of the partial template."""
        request = self.factory.get(
            self.endpoint, headers={"HX-Request": True, "HX-Boosted": False}
        )
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        view.render_to_response(view.get_context_data())
        self.assertIn("/partials/_", view.template_name)

    def test_get_context_data(self) -> None:
        """Fails if the view context didn't have ``customer`` (doesn't need ``title``)."""
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn("customer", context)


class HomeViewTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.client = Client()
        self.endpoint = "/"
        self.view_cls = views.HomeView

    def test_htmx_renders_partial_template(self) -> None:
        """Fails if an HTMX request renders the main template instead of the partial template."""
        request = self.factory.get(
            self.endpoint, headers={"HX-Request": True, "HX-Boosted": False}
        )
        view = self.view_cls()
        view.setup(request)
        view.render_to_response(view.get_context_data())
        self.assertIn("/partials/_", view.template_name)

    def test_get_context_data(self) -> None:
        """Fails if ``title`` wasn't in the view context."""
        request = self.factory.get(self.endpoint)
        view = self.view_cls()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn("title", context)


class TermsViewTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.client = Client()
        self.endpoint = "/terms/"
        self.view_cls = views.TermsView

    def test_htmx_renders_partial_template(self) -> None:
        """Fails if an HTMX request renders the main template instead of the partial template."""
        request = self.factory.get(
            self.endpoint, headers={"HX-Request": True, "HX-Boosted": False}
        )
        view = self.view_cls()
        view.setup(request)
        view.render_to_response(view.get_context_data())
        self.assertIn("/partials/_", view.template_name)

    def test_get_context_data(self) -> None:
        """Fails if ``title`` wasn't in the view context."""
        request = self.factory.get(self.endpoint)
        view = self.view_cls()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn("title", context)


class ContactViewTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.client = Client()
        self.endpoint = "/contact/"
        self.view_cls = views.ContactView

    def test_htmx_renders_partial_template(self) -> None:
        """Fails if an HTMX request renders the main template instead of the partial template."""
        request = self.factory.get(
            self.endpoint, headers={"HX-Request": True, "HX-Boosted": False}
        )
        view = self.view_cls()
        view.setup(request)
        view.render_to_response(view.get_context_data())
        self.assertIn("/partials/_", view.template_name)

    def test_get_context_data(self) -> None:
        """Fails if ``title`` wasn't in the view context."""
        request = self.factory.get(self.endpoint)
        view = self.view_cls()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn("title", context)


class PrivacyViewTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.client = Client()
        self.endpoint = "/privacy/"
        self.view_cls = views.PrivacyView

    def test_htmx_renders_partial_template(self) -> None:
        """Fails if an HTMX request renders the main template instead of the partial template."""
        request = self.factory.get(
            self.endpoint, headers={"HX-Request": True, "HX-Boosted": False}
        )
        view = self.view_cls()
        view.setup(request)
        view.render_to_response(view.get_context_data())
        self.assertIn("/partials/_", view.template_name)

    def test_get_context_data(self) -> None:
        """Fails if ``title`` wasn't in the view context."""
        request = self.factory.get(self.endpoint)
        view = self.view_cls()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn("title", context)


class LoginViewTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.client = Client()
        self.endpoint = "/login/"
        self.view_cls = views.LoginView

    def test_htmx_renders_partial_template(self) -> None:
        """Fails if an HTMX request renders the main template instead of the partial template."""
        request = self.factory.get(
            self.endpoint, headers={"HX-Request": True, "HX-Boosted": False}
        )
        view = self.view_cls()
        view.setup(request)
        view.render_to_response(view.get_context_data())
        self.assertIn("/partials/_", view.template_name)

    def test_get_initial(self) -> None:
        """Fails if ``username`` was passed as a path parameter but wasn't added to the form as the initial username."""
        test_username = "testuser@testdomain.com"
        request = self.factory.get(
            self.endpoint, query_params={"username": test_username}
        )
        view = self.view_cls()
        view.setup(request)
        initial = view.get_initial()
        self.assertIn("username", initial)
        self.assertEqual(initial["username"], test_username)

    def test_get_context_data(self) -> None:
        """Fails if ``title`` wasn't in the view context."""
        request = self.factory.get(self.endpoint)
        view = self.view_cls()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn("title", context)


class WialonNotificationUnitSelectFormViewTestCase(TestCase):
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
        self.test_token = models.WialonToken.objects.create(
            customer=self.test_customer, name=os.getenv("WIALON_TOKEN")
        )
        self.factory = RequestFactory()
        self.client = Client()
        self.endpoint = "/notifications/units/select/"
        self.view_cls = views.WialonNotificationUnitSelectFormView

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

    def test_htmx_renders_partial_template(self) -> None:
        """Fails if an HTMX request renders the main template instead of the partial template."""
        request = self.factory.get(
            self.endpoint, headers={"HX-Request": True, "HX-Boosted": False}
        )
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        view.render_to_response(view.get_context_data())
        self.assertIn("/partials/_", view.template_name)

    def test_get_form(self) -> None:
        """Fails if the form's unit list was unpopulated."""
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        form = view.get_form()
        # TODO: Test form

    def test_form_valid(self) -> None:
        """Fails if the ``un`` path parameter wasn't added to the URL before redirecting the client."""
        request = self.factory.get(self.endpoint)
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        form = view.get_form(form_class=None)
        # TODO: Test form


class WialonNotificationTriggerSelectFormViewTestCase(TestCase):
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
        self.endpoint = "/notifications/triggers/select/"
        self.view_cls = views.WialonNotificationTriggerSelectFormView

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

    def test_htmx_renders_partial_template(self) -> None:
        """Fails if an HTMX request renders the main template instead of the partial template."""
        request = self.factory.get(
            self.endpoint, headers={"HX-Request": True, "HX-Boosted": False}
        )
        request.user = self.test_user
        view = self.view_cls()
        view.setup(request)
        view.render_to_response(view.get_context_data())
        self.assertIn("/partials/_", view.template_name)
