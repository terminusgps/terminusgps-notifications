import decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from terminusgps_notifications.models import TerminusgpsNotificationsCustomer


class TerminusgpsNotificationsCustomerTestCase(TestCase):
    def setUp(self) -> None:
        self.test_company = "Test Company"
        self.test_resource_id = "12345678"

        self.user = get_user_model().objects.create_user(
            username="testuser@terminusgps.com",
            email="testuser@terminusgps.com",
            password="super_secure_password1!",
        )
        self.customer = TerminusgpsNotificationsCustomer.objects.create(
            user=self.user,
            company=self.test_company,
            resource_id=self.test_resource_id,
        )

    def test_customer_str_method(self) -> None:
        """Fails if the result of calling :py:func:`str` on the customer isn't equal to the user's username."""
        self.assertEqual(str(self.customer), str(self.user.username))

    def test_default_values(self) -> None:
        """Fails if the expected default values weren't set on the customer."""
        self.assertEqual(self.customer.user, self.user)
        self.assertEqual(self.customer.company, self.test_company)
        self.assertEqual(self.customer.resource_id, self.test_resource_id)
        self.assertEqual(self.customer.date_format, "%Y-%m-%d %H:%M:%S")
        self.assertEqual(self.customer.max_sms_count, 500)
        self.assertEqual(self.customer.max_voice_count, 500)
        self.assertEqual(self.customer.sms_count, 0)
        self.assertEqual(self.customer.voice_count, 0)
        self.assertAlmostEqual(
            float(self.customer.tax_rate),
            float(decimal.Decimal("0.0825")),
            places=2,
        )
        self.assertAlmostEqual(
            float(self.customer.subtotal),
            float(decimal.Decimal("64.99")),
            places=2,
        )

    def test_generated_tax_calculation(self) -> None:
        """Fails if the automatically generated tax amount was incorrectly calculated."""
        self.customer.refresh_from_db()
        expected_tax = (
            self.customer.subtotal * (self.customer.tax_rate + 1)
            - self.customer.subtotal
        )
        self.assertAlmostEqual(
            float(self.customer.tax), float(expected_tax), places=2
        )

    def test_generated_grand_total_calculation(self) -> None:
        """Fails if the automatically generated grand total amount was incorrectly calculated."""
        self.customer.refresh_from_db()
        expected_grand_total = self.customer.subtotal * (
            self.customer.tax_rate + 1
        )
        self.assertAlmostEqual(
            float(self.customer.grand_total),
            float(expected_grand_total),
            places=2,
        )
