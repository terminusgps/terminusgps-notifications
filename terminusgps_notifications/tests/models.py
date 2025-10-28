from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from terminusgps.authorizenet.constants import Environment, ValidationMode

from terminusgps_notifications.models import (
    TerminusgpsNotificationsCustomer,
    WialonNotification,
)


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

    def test_get_units_from_wialon(self) -> None:
        """Fails if the method doesn't return the expected Wialon API response."""
        mock_response = {
            "items": [
                {
                    "nm": "Unit #1",
                    "cls": 2,
                    "id": 12345678,
                    "mu": 1,
                    "uacl": 4178867978239,
                },
                {
                    "nm": "Unit #2",
                    "cls": 2,
                    "id": 23456781,
                    "mu": 1,
                    "uacl": 4178867978239,
                },
                {
                    "nm": "Unit #3",
                    "cls": 2,
                    "id": 34567812,
                    "mu": 1,
                    "uacl": 4178867978239,
                },
                {
                    "nm": "Unit #4",
                    "cls": 2,
                    "id": 45678123,
                    "mu": 1,
                    "uacl": 4178867978239,
                },
            ]
        }
        mock_session = Mock()
        mock_wialon_api = Mock()
        mock_session.wialon_api = mock_wialon_api
        mock_session.wialon_api.core_search_items.return_value = mock_response
        self.assertEqual(
            mock_response.get("items", []),
            self.test_customer.get_units_from_wialon(mock_session),
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
        self.test_customer = TerminusgpsNotificationsCustomer.objects.create(
            user=self.test_user
        )
        self.test_notification = WialonNotification(
            customer=self.test_customer,
            name="Test Notification",
            message="%NOTIFICATION%",
            method="sms",
            unit_list="[12345678, 56781234]",
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
