import unittest
from unittest.mock import patch, MagicMock
from revcontent_api import RevcontentAPI

class TestRevcontentAPI(unittest.TestCase):

    @patch("requests.post")
    def test_auth_success(self, mock_post):
        """Test successful authentication."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"access_token": "mock_token"}
        mock_post.return_value = mock_resp
        mock_resp.text = str(mock_resp.json.return_value)

        api = RevcontentAPI("id", "secret")
        api.auth()
        self.assertEqual(api.access_token, "mock_token")

    @patch("requests.post")
    def test_auth_failure_400(self, mock_post):
        """Test authentication failure (400 error)."""
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.json.return_value = {
            "error": "invalid_client",
            "error_description": "Client authentication failed"
        }
        mock_resp.text = str(mock_resp.json.return_value)
        mock_post.return_value = mock_resp

        api = RevcontentAPI("bad", "bad")
        with self.assertRaises(ValueError) as cm:
            api.auth()
        self.assertIn("Authentication failed with 400 Bad Request", str(cm.exception))

    @patch("requests.post")
    def test_auth_failure_no_token(self, mock_post):
        """Test authentication failure (no token in response)."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {}
        mock_post.return_value = mock_resp
        mock_resp.text = str(mock_resp.json.return_value)

        api = RevcontentAPI("id", "secret")
        with self.assertRaises(Exception) as cm:
            api.auth()
        self.assertIn("Access token not found", str(cm.exception))

    @patch("requests.post")
    def test_create_campaign_no_auth(self, mock_post):
        """Test creating campaign without authentication."""
        api = RevcontentAPI("id", "secret")
        with self.assertRaises(Exception):
            api.create_campaign("test", 50, 0.1, ["US"])

    @patch("requests.post")
    def test_create_campaign_success(self, mock_post):
        """Test successful campaign creation."""
        # Mock campaign creation response
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"data": [{"id": "test_campaign_id"}]}
        mock_resp.text = str(mock_resp.json.return_value)
        mock_post.return_value = mock_resp

        api = RevcontentAPI("id", "secret")
        api.access_token = "mock_token"  # Simulate already authenticated
        campaign_id = api.create_campaign("test", 50, 0.1, ["US"])
        self.assertEqual(campaign_id, "test_campaign_id")

    @patch("requests.post")
    def test_create_campaign_no_id_in_response(self, mock_post):
        """Test campaign creation with missing campaign ID."""
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"data": [{}]}
        mock_post.return_value = mock_resp
        mock_resp.text = str(mock_resp.json.return_value)

        api = RevcontentAPI("id", "secret")
        api.access_token = "mock_token"
        with self.assertRaises(Exception) as cm:
            api.create_campaign("test", 50, 0.1, ["US"])
        self.assertIn("does not contain campaign ID", str(cm.exception))

    @patch("requests.get")
    def test_get_campaign_stats_success(self, mock_get):
        """Test fetching campaign stats successfully."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [{
                "status": "active",
                "impressions": 123,
                "clicks": 4
            }]
        }
        mock_resp.text = str(mock_resp.json.return_value)
        mock_get.return_value = mock_resp

        api = RevcontentAPI("id", "secret")
        api.access_token = "mock_token"
        stats = api.get_campaign_stats_by_id("test_campaign_id")
        self.assertIsInstance(stats, list)
        self.assertEqual(stats[0]["status"], "active")
        self.assertEqual(stats[0]["impressions"], 123)
        self.assertEqual(stats[0]["clicks"], 4)

    @patch("requests.get")
    def test_get_campaign_stats_no_data(self, mock_get):
        """Test fetching stats returns no data key."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {}
        mock_get.return_value = mock_resp
        mock_resp.text = str(mock_resp.json.return_value)

        api = RevcontentAPI("id", "secret")
        api.access_token = "mock_token"
        with self.assertRaises(Exception) as cm:
            api.get_campaign_stats_by_id("test_campaign_id")
        self.assertIn('does not contain "data" key', str(cm.exception))

    @patch("requests.get")
    def test_get_campaign_stats_error(self, mock_get):
        """Test stats fetching error (simulate 400)."""
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.json.return_value = {
            "errors": [{
                "code": 400,
                "title": "Invalid Parameters",
                "detail": "Invalid campaign ID"
            }]
        }
        mock_resp.text = str(mock_resp.json.return_value)
        mock_get.return_value = mock_resp

        api = RevcontentAPI("id", "secret")
        api.access_token = "mock_token"
        with self.assertRaises(ValueError) as cm:
            api.get_campaign_stats_by_id("wrong_id")
        self.assertIn("400 Bad Request", str(cm.exception))
        self.assertIn("Invalid Parameters", str(cm.exception))

if __name__ == "__main__":
    unittest.main()
