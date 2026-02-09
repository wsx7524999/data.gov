"""
Cloud.gov connection module for Data.gov

This module provides functionality to connect to cloud.gov platform,
authenticate using API keys, and release datasets programmatically.
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()

# Cloud.gov API configuration
CLOUDGOV_API_URL = os.getenv("CLOUDGOV_API_URL", "https://api.fr.cloud.gov")
CLOUDGOV_API_KEY = os.getenv("CLOUDGOV_API_KEY")
CLOUDGOV_API_SECRET = os.getenv("CLOUDGOV_API_SECRET")
CLOUDGOV_ORG = os.getenv("CLOUDGOV_ORG")
CLOUDGOV_SPACE = os.getenv("CLOUDGOV_SPACE")


class CloudGovClient:
    """Client for interacting with cloud.gov API"""

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        org: Optional[str] = None,
        space: Optional[str] = None,
    ):
        """
        Initialize cloud.gov client

        Args:
            api_url: Cloud.gov API URL
            api_key: API key for authentication
            api_secret: API secret for authentication
            org: Organization name
            space: Space name
        """
        self.api_url = api_url or CLOUDGOV_API_URL
        self.api_key = api_key or CLOUDGOV_API_KEY
        self.api_secret = api_secret or CLOUDGOV_API_SECRET
        self.org = org or CLOUDGOV_ORG
        self.space = space or CLOUDGOV_SPACE
        self.token = None
        self.session = requests.Session()

    def authenticate(self) -> bool:
        """
        Authenticate with cloud.gov API

        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self.api_key or not self.api_secret:
            print("Error: API key and secret are required for authentication")
            return False

        try:
            # Use OAuth2 authentication flow
            auth_url = f"{self.api_url}/oauth/token"
            response = self.session.post(
                auth_url,
                auth=(self.api_key, self.api_secret),
                data={"grant_type": "client_credentials"},
            )

            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                self.session.headers.update(
                    {"Authorization": f"Bearer {self.token}"}
                )
                print("Successfully authenticated with cloud.gov")
                return True
            else:
                print(
                    f"Authentication failed with status code: {response.status_code}"
                )
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"Error during authentication: {str(e)}")
            return False

    def get_datasets(self) -> List[Dict[str, Any]]:
        """
        Fetch datasets from cloud.gov

        Returns:
            List of datasets
        """
        if not self.token:
            if not self.authenticate():
                return []

        try:
            # Example endpoint - adjust based on actual cloud.gov API
            datasets_url = f"{self.api_url}/v3/apps"
            response = self.session.get(datasets_url)

            if response.status_code == 200:
                data = response.json()
                datasets = data.get("resources", [])
                print(f"Successfully fetched {len(datasets)} datasets")
                return datasets
            else:
                print(f"Failed to fetch datasets: {response.status_code}")
                return []

        except Exception as e:
            print(f"Error fetching datasets: {str(e)}")
            return []

    def release_dataset(self, dataset_id: str, metadata: Optional[Dict] = None) -> bool:
        """
        Release a dataset through cloud.gov

        Args:
            dataset_id: ID of the dataset to release
            metadata: Optional metadata to include with the release

        Returns:
            bool: True if release successful, False otherwise
        """
        if not self.token:
            if not self.authenticate():
                return False

        try:
            # Load user metadata if available
            if not metadata:
                metadata = self._load_user_metadata()

            release_data = {
                "dataset_id": dataset_id,
                "status": "released",
                "metadata": metadata,
                "org": self.org,
                "space": self.space,
            }

            # Example endpoint - adjust based on actual cloud.gov API
            release_url = f"{self.api_url}/v3/datasets/{dataset_id}/release"
            response = self.session.post(release_url, json=release_data)

            if response.status_code in [200, 201, 202]:
                print(f"Successfully released dataset: {dataset_id}")
                return True
            else:
                print(f"Failed to release dataset: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"Error releasing dataset: {str(e)}")
            return False

    def _load_user_metadata(self) -> Dict[str, Any]:
        """
        Load user metadata from metadata.json file

        Returns:
            Dictionary containing user metadata
        """
        try:
            metadata_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "metadata.json"
            )
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    return json.load(f)
            else:
                print(f"Metadata file not found at {metadata_path}")
                return {}
        except Exception as e:
            print(f"Error loading metadata: {str(e)}")
            return {}

    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get current connection status

        Returns:
            Dictionary with connection status information
        """
        return {
            "api_url": self.api_url,
            "authenticated": self.token is not None,
            "org": self.org,
            "space": self.space,
        }


def main():
    """Main function to demonstrate cloud.gov integration"""
    print("=== Cloud.gov Integration Demo ===\n")

    # Initialize client
    client = CloudGovClient()

    # Display connection status
    status = client.get_connection_status()
    print(f"API URL: {status['api_url']}")
    print(f"Organization: {status['org']}")
    print(f"Space: {status['space']}")
    print(f"Authenticated: {status['authenticated']}\n")

    # Authenticate
    if client.authenticate():
        print("\n=== Fetching Datasets ===")
        datasets = client.get_datasets()

        if datasets:
            print(f"\nFound {len(datasets)} datasets")
            # Example: Release first dataset
            if len(datasets) > 0:
                dataset_id = datasets[0].get("guid", "example-dataset-id")
                print(f"\n=== Releasing Dataset: {dataset_id} ===")
                client.release_dataset(dataset_id)
        else:
            print("No datasets found or unable to fetch datasets")
    else:
        print("Authentication failed. Please check your API credentials.")


if __name__ == "__main__":
    main()
