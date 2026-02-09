"""
Unit tests for cloud.gov integration module

These tests verify the CloudGovClient functionality without requiring
actual cloud.gov credentials or network access.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datagov_metrics.cloudgov import CloudGovClient


class TestCloudGovClient(unittest.TestCase):
    """Test cases for CloudGovClient class"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = CloudGovClient(
            api_url="https://test.api.cloud.gov",
            api_key="test-key",
            api_secret="test-secret",
            org="test-org",
            space="test-space",
        )

    def test_initialization(self):
        """Test client initialization"""
        self.assertEqual(self.client.api_url, "https://test.api.cloud.gov")
        self.assertEqual(self.client.api_key, "test-key")
        self.assertEqual(self.client.api_secret, "test-secret")
        self.assertEqual(self.client.org, "test-org")
        self.assertEqual(self.client.space, "test-space")
        self.assertIsNone(self.client.token)

    def test_initialization_from_env(self):
        """Test client initialization from environment variables"""
        with patch.dict(
            os.environ,
            {
                "CLOUDGOV_API_URL": "https://env.api.cloud.gov",
                "CLOUDGOV_API_KEY": "env-key",
                "CLOUDGOV_API_SECRET": "env-secret",
                "CLOUDGOV_ORG": "env-org",
                "CLOUDGOV_SPACE": "env-space",
            },
        ):
            client = CloudGovClient()
            self.assertEqual(client.api_url, "https://env.api.cloud.gov")
            self.assertEqual(client.api_key, "env-key")
            self.assertEqual(client.api_secret, "env-secret")
            self.assertEqual(client.org, "env-org")
            self.assertEqual(client.space, "env-space")

    @patch("datagov_metrics.cloudgov.requests.Session")
    def test_authenticate_success(self, mock_session_class):
        """Test successful authentication"""
        # Mock the session and response
        mock_session = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test-token"}
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Create new client with mocked session
        client = CloudGovClient(
            api_url="https://test.api.cloud.gov",
            api_key="test-key",
            api_secret="test-secret",
        )

        result = client.authenticate()

        self.assertTrue(result)
        self.assertEqual(client.token, "test-token")
        mock_session.post.assert_called_once()

    @patch("datagov_metrics.cloudgov.requests.Session")
    def test_authenticate_failure(self, mock_session_class):
        """Test authentication failure"""
        # Mock the session and response
        mock_session = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Create new client with mocked session
        client = CloudGovClient(
            api_url="https://test.api.cloud.gov",
            api_key="test-key",
            api_secret="test-secret",
        )

        result = client.authenticate()

        self.assertFalse(result)
        self.assertIsNone(client.token)

    def test_authenticate_no_credentials(self):
        """Test authentication without credentials"""
        client = CloudGovClient(api_url="https://test.api.cloud.gov")
        result = client.authenticate()

        self.assertFalse(result)

    def test_get_connection_status(self):
        """Test getting connection status"""
        status = self.client.get_connection_status()

        self.assertEqual(status["api_url"], "https://test.api.cloud.gov")
        self.assertEqual(status["org"], "test-org")
        self.assertEqual(status["space"], "test-space")
        self.assertFalse(status["authenticated"])

        # Test with token
        self.client.token = "test-token"
        status = self.client.get_connection_status()
        self.assertTrue(status["authenticated"])

    @patch("datagov_metrics.cloudgov.requests.Session")
    def test_get_datasets(self, mock_session_class):
        """Test fetching datasets"""
        # Mock the session and responses
        mock_session = MagicMock()
        
        # Mock authentication response
        auth_response = Mock()
        auth_response.status_code = 200
        auth_response.json.return_value = {"access_token": "test-token"}
        
        # Mock datasets response
        datasets_response = Mock()
        datasets_response.status_code = 200
        datasets_response.json.return_value = {
            "resources": [
                {"guid": "dataset-1", "name": "Dataset 1"},
                {"guid": "dataset-2", "name": "Dataset 2"},
            ]
        }
        
        mock_session.post.return_value = auth_response
        mock_session.get.return_value = datasets_response
        mock_session_class.return_value = mock_session

        # Create new client with mocked session
        client = CloudGovClient(
            api_url="https://test.api.cloud.gov",
            api_key="test-key",
            api_secret="test-secret",
        )

        datasets = client.get_datasets()

        self.assertEqual(len(datasets), 2)
        self.assertEqual(datasets[0]["guid"], "dataset-1")
        self.assertEqual(datasets[1]["guid"], "dataset-2")

    @patch("datagov_metrics.cloudgov.requests.Session")
    @patch("builtins.open", create=True)
    def test_release_dataset(self, mock_open, mock_session_class):
        """Test releasing a dataset"""
        # Mock the session and responses
        mock_session = MagicMock()
        
        # Mock authentication response
        auth_response = Mock()
        auth_response.status_code = 200
        auth_response.json.return_value = {"access_token": "test-token"}
        
        # Mock release response
        release_response = Mock()
        release_response.status_code = 201
        
        mock_session.post.side_effect = [auth_response, release_response]
        mock_session_class.return_value = mock_session

        # Mock metadata file
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps({
            "name": "Test User",
            "dob": "2000-01-01"
        })
        mock_open.return_value = mock_file

        # Create new client with mocked session
        client = CloudGovClient(
            api_url="https://test.api.cloud.gov",
            api_key="test-key",
            api_secret="test-secret",
            org="test-org",
            space="test-space",
        )

        result = client.release_dataset("dataset-123")

        self.assertTrue(result)

    @patch("os.path.exists")
    @patch("builtins.open", create=True)
    def test_load_user_metadata(self, mock_open, mock_exists):
        """Test loading user metadata"""
        # Mock metadata file exists
        mock_exists.return_value = True
        
        # Mock file contents
        metadata = {"name": "Test User", "dob": "2000-01-01"}
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps(metadata)
        mock_open.return_value = mock_file

        result = self.client._load_user_metadata()

        self.assertEqual(result["name"], "Test User")
        self.assertEqual(result["dob"], "2000-01-01")

    @patch("os.path.exists")
    def test_load_user_metadata_no_file(self, mock_exists):
        """Test loading user metadata when file doesn't exist"""
        mock_exists.return_value = False

        result = self.client._load_user_metadata()

        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
