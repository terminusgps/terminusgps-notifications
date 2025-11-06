from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from terminusgps.authorizenet.constants import Environment, ValidationMode

from terminusgps_notifications import models


@override_settings(
    MERCHANT_AUTH_ENVIRONMENT=Environment.SANDBOX,
    MERCHANT_AUTH_VALIDATION_MODE=ValidationMode.TEST,
)
class TerminusgpsNotificationsCustomerTestCase(TestCase):
    def setUp(self) -> None:
        self.test_company = "Test Company"
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
                user=self.test_user, company=self.test_company
            )
        )

    def tearDown(self) -> None:
        self.test_user.delete()

    def test_str(self) -> None:
        """Fails if the result of calling :py:func:`str` on the customer isn't equal to the user's username."""
        self.assertEqual(str(self.test_customer), str(self.test_user.username))

    def test_tax(self) -> None:
        """Fails if the automatically generated tax amount was incorrectly calculated."""
        self.test_customer.refresh_from_db()
        expected_tax = (
            self.test_customer.subtotal * (self.test_customer.tax_rate + 1)
            - self.test_customer.subtotal
        )
        self.assertAlmostEqual(
            float(self.test_customer.tax), float(expected_tax), places=2
        )

    def test_grand_total(self) -> None:
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


class WialonNotificationTestCase(TestCase):
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
        self.test_notification = models.WialonNotification(
            customer=self.test_customer,
            name="Test Notification",
            message="%NOTIFICATION%",
            method="sms",
            unit_list=[12345678, 56781234],
            trigger={
                "trg": {
                    "t": "sensor_value",
                    "p": {
                        "lower_bound": "-1.0",
                        "merge": 0,
                        "prev_msg_diff": 0,
                        "sensor_name_mask": "*IGN*",
                        "sensor_type": "engine operation",
                        "type": 0,
                        "upper_bound": "1.0",
                    },
                }
            },
        )
        self.test_notification.actions = self.test_notification.get_actions()
        self.test_notification.text = self.test_notification.get_text()
        # TODO: Create notification in Wialon before testing

    def tearDown(self) -> None:
        self.test_user.delete()
