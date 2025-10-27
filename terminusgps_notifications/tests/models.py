import decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from terminusgps.authorizenet.constants import Environment, ValidationMode

from terminusgps_notifications.models import TerminusgpsNotificationsCustomer


@override_settings(
    MERCHANT_AUTH_ENVIRONMENT=Environment.SANDBOX,
    MERCHANT_AUTH_VALIDATION_MODE=ValidationMode.TEST,
)
class TerminusgpsNotificationsCustomerTestCase(TestCase):
    def setUp(self) -> None:
        self.test_company = "Test Company"
        self.test_resource_id = "12345678"
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
        self.test_customer = TerminusgpsNotificationsCustomer.objects.create(
            user=self.test_user,
            company=self.test_company,
            resource_id=self.test_resource_id,
        )

    def tearDown(self) -> None:
        self.test_user.delete()

    def test_customer_str(self) -> None:
        """Fails if the result of calling :py:func:`str` on the customer isn't equal to the user's username."""
        self.assertEqual(str(self.test_customer), str(self.test_user.username))

    def test_default_values(self) -> None:
        """Fails if the expected default values weren't set on the customer."""
        self.assertEqual(self.test_customer.date_format, "%Y-%m-%d %H:%M:%S")
        self.assertEqual(self.test_customer.max_sms_count, 500)
        self.assertEqual(self.test_customer.max_voice_count, 500)
        self.assertEqual(self.test_customer.sms_count, 0)
        self.assertEqual(self.test_customer.voice_count, 0)
        self.assertAlmostEqual(
            float(self.test_customer.tax_rate),
            float(decimal.Decimal("0.0825")),
            places=2,
        )
        self.assertAlmostEqual(
            float(self.test_customer.subtotal),
            float(decimal.Decimal("64.99")),
            places=2,
        )

    def test_generated_tax_calculation(self) -> None:
        """Fails if the automatically generated tax amount was incorrectly calculated."""
        self.test_customer.refresh_from_db()
        expected_tax = (
            self.test_customer.subtotal * (self.test_customer.tax_rate + 1)
            - self.test_customer.subtotal
        )
        self.assertAlmostEqual(
            float(self.test_customer.tax), float(expected_tax), places=2
        )

    def test_generated_grand_total_calculation(self) -> None:
        """Fails if the automatically generated grand total amount was incorrectly calculated."""
        self.test_customer.refresh_from_db()
        expected_grand_total = self.test_customer.subtotal * (
            self.test_customer.tax_rate + 1
        )
        self.assertAlmostEqual(
            float(self.test_customer.grand_total),
            float(expected_grand_total),
            places=2,
        )
