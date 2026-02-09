#!/usr/bin/env python3
"""
Dataset Release Script

This script automates the process of releasing datasets from cloud.gov.
It can be run manually or scheduled as part of a CI/CD pipeline.

Usage:
    python release_datasets.py [--dataset-id DATASET_ID] [--all]

Examples:
    # Release a specific dataset
    python release_datasets.py --dataset-id abc123

    # Release all available datasets
    python release_datasets.py --all

    # Display help
    python release_datasets.py --help
"""

import argparse
import sys
import os

# Add parent directory to path to import datagov_metrics
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datagov_metrics.cloudgov import CloudGovClient


def release_single_dataset(client: CloudGovClient, dataset_id: str) -> bool:
    """
    Release a single dataset

    Args:
        client: CloudGovClient instance
        dataset_id: ID of the dataset to release

    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n=== Releasing Dataset: {dataset_id} ===")
    success = client.release_dataset(dataset_id)

    if success:
        print(f"✓ Successfully released dataset: {dataset_id}")
    else:
        print(f"✗ Failed to release dataset: {dataset_id}")

    return success


def release_all_datasets(client: CloudGovClient) -> bool:
    """
    Release all available datasets

    Args:
        client: CloudGovClient instance

    Returns:
        bool: True if all releases successful, False otherwise
    """
    print("\n=== Fetching All Datasets ===")
    datasets = client.get_datasets()

    if not datasets:
        print("No datasets found to release")
        return False

    print(f"Found {len(datasets)} datasets to release\n")

    success_count = 0
    fail_count = 0

    for dataset in datasets:
        dataset_id = dataset.get("guid", dataset.get("id", "unknown"))
        if release_single_dataset(client, dataset_id):
            success_count += 1
        else:
            fail_count += 1

    print(f"\n=== Release Summary ===")
    print(f"Total datasets: {len(datasets)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")

    return fail_count == 0


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Release datasets from cloud.gov",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dataset-id", type=str, help="ID of the dataset to release", default=None
    )

    parser.add_argument(
        "--all", action="store_true", help="Release all available datasets"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.dataset_id and not args.all:
        parser.error("Either --dataset-id or --all must be specified")

    if args.dataset_id and args.all:
        parser.error("Cannot specify both --dataset-id and --all")

    print("=== Cloud.gov Dataset Release Tool ===\n")

    # Initialize client
    client = CloudGovClient()

    # Display connection status
    status = client.get_connection_status()
    print(f"API URL: {status['api_url']}")
    print(f"Organization: {status['org']}")
    print(f"Space: {status['space']}")

    # Authenticate
    if not client.authenticate():
        print("\n✗ Authentication failed. Please check your API credentials.")
        sys.exit(1)

    print("✓ Authentication successful\n")

    # Perform release operation
    if args.dataset_id:
        success = release_single_dataset(client, args.dataset_id)
    else:
        success = release_all_datasets(client)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
