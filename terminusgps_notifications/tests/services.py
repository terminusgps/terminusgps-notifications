from urllib.parse import quote

from django.test import TestCase, override_settings

from terminusgps_notifications import services


class GetWialonRedirectUriTestCase(TestCase):
    @override_settings(DEBUG=False)
    def test_production_redirect_uri(self) -> None:
        """Fails if the function returns anything other than the production URL when DEBUG is false."""
        result = services.get_wialon_redirect_uri()
        self.assertTrue(result.startswith("https://api.terminusgps.com/"))
        self.assertIn("/account", result)

    @override_settings(DEBUG=True)
    def test_development_redirect_uri(self) -> None:
        """Fails if the function returns anything other than the development URL when DEBUG is true."""
        result = services.get_wialon_redirect_uri()
        self.assertTrue(result.startswith("http://127.0.0.1:8000/"))
        self.assertIn("/account", result)


class GetWialonLoginParametersTestCase(TestCase):
    def test_returns_correct_query_string(self) -> None:
        """Fails if the function returns anything other than a valid query string for the Wialon login page."""
        username = "testuser@terminusgps.com"
        result = services.get_wialon_login_parameters(username)
        self.assertIn("client_id=", result)
        self.assertIn("access_type=", result)
        self.assertIn("activation_time=", result)
        self.assertIn("duration=", result)
        self.assertIn("lang=", result)
        self.assertIn("flags=", result)
        self.assertIn(f"user={quote(username)}", result)
        self.assertIn("response_type=", result)

    @override_settings(WIALON_TOKEN_ACCESS_TYPE=1)
    def test_uses_access_type_from_settings(self) -> None:
        """Fails if the query string contains an access type other than 1."""
        username = "testuser@terminusgps.com"
        result = services.get_wialon_login_parameters(username)
        self.assertIn("access_type=1", result)
