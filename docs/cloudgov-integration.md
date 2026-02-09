# Cloud.gov Integration

This documentation describes the cloud.gov integration features added to the Data.gov repository.

## Overview

The cloud.gov integration provides the following capabilities:

1. **Secure Connection to cloud.gov**: Establishes authenticated connections to the cloud.gov platform
2. **Dataset Management**: Fetch and manage datasets stored in cloud.gov
3. **Automated Dataset Release**: Programmatically release datasets through the application
4. **Metadata Integration**: Include user metadata with dataset releases

## Features

### 1. Cloud.gov Connection

The `CloudGovClient` class in `metrics/datagov_metrics/cloudgov.py` provides a secure connection to cloud.gov using API keys and OAuth2 authentication.

#### Configuration

Configure the connection using environment variables in `metrics/.env`:

```bash
CLOUDGOV_API_URL=https://api.fr.cloud.gov
CLOUDGOV_API_KEY=your-api-key-here
CLOUDGOV_API_SECRET=your-api-secret-here
CLOUDGOV_ORG=your-organization-name
CLOUDGOV_SPACE=your-space-name
```

An example configuration file is provided at `metrics/.env.example`. Copy this file to `metrics/.env` and update with your actual credentials.

**Security Note**: Never commit `.env` files to version control. The `.gitignore` file is configured to exclude `.env` files (except for the example).

### 2. Metadata Integration

User metadata is stored in `metadata.json` at the root of the repository:

```json
{
  "name": "BAO THANH HANG LAM",
  "dob": "1971-01-03",
  "created_at": "2026-02-09",
  "description": "User metadata for cloud.gov data release integration"
}
```

This metadata is automatically included when releasing datasets and can be customized as needed.

### 3. Dataset Release Functionality

#### Using the CloudGovClient Class

```python
from datagov_metrics.cloudgov import CloudGovClient

# Initialize client
client = CloudGovClient()

# Authenticate
if client.authenticate():
    # Fetch datasets
    datasets = client.get_datasets()
    
    # Release a dataset
    dataset_id = "your-dataset-id"
    client.release_dataset(dataset_id)
```

#### Using the Command-Line Script

The `release_datasets.py` script provides a command-line interface for dataset releases:

```bash
# Release a specific dataset
python metrics/release_datasets.py --dataset-id abc123

# Release all available datasets
python metrics/release_datasets.py --all

# Display help
python metrics/release_datasets.py --help
```

## API Reference

### CloudGovClient Class

#### Constructor

```python
CloudGovClient(
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None,
    org: Optional[str] = None,
    space: Optional[str] = None
)
```

Creates a new cloud.gov client instance. All parameters are optional and default to environment variables if not provided.

#### Methods

##### `authenticate() -> bool`

Authenticates with the cloud.gov API using OAuth2 client credentials flow.

**Returns**: `True` if authentication successful, `False` otherwise

##### `get_datasets() -> List[Dict[str, Any]]`

Fetches all datasets from cloud.gov.

**Returns**: List of dataset objects

##### `release_dataset(dataset_id: str, metadata: Optional[Dict] = None) -> bool`

Releases a specific dataset.

**Parameters**:
- `dataset_id`: ID of the dataset to release
- `metadata`: Optional custom metadata (defaults to loading from `metadata.json`)

**Returns**: `True` if release successful, `False` otherwise

##### `get_connection_status() -> Dict[str, Any]`

Returns the current connection status.

**Returns**: Dictionary with connection information

## Installation

### Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)

### Setup

1. Navigate to the metrics directory:
   ```bash
   cd metrics
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Copy the example environment file and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

## Usage Examples

### Example 1: Basic Connection Test

```python
from datagov_metrics.cloudgov import CloudGovClient

client = CloudGovClient()
status = client.get_connection_status()
print(f"Connected to: {status['api_url']}")

if client.authenticate():
    print("Authentication successful!")
```

### Example 2: Fetch and List Datasets

```python
from datagov_metrics.cloudgov import CloudGovClient

client = CloudGovClient()

if client.authenticate():
    datasets = client.get_datasets()
    print(f"Found {len(datasets)} datasets:")
    for dataset in datasets:
        print(f"  - {dataset.get('name', 'Unnamed')}")
```

### Example 3: Release Dataset with Custom Metadata

```python
from datagov_metrics.cloudgov import CloudGovClient

client = CloudGovClient()

if client.authenticate():
    custom_metadata = {
        "name": "BAO THANH HANG LAM",
        "dob": "1971-01-03",
        "release_version": "1.0",
        "notes": "Initial release"
    }
    
    client.release_dataset("dataset-123", metadata=custom_metadata)
```

### Example 4: Automated Release Script

```bash
#!/bin/bash
# Release all datasets in production

cd metrics
python release_datasets.py --all

if [ $? -eq 0 ]; then
    echo "All datasets released successfully"
else
    echo "Some datasets failed to release"
    exit 1
fi
```

## Integration with Existing Metrics

The cloud.gov module follows the same patterns as existing metrics modules (`ga.py` and `ckan.py`):

- Uses `dotenv` for environment configuration
- Provides a `main()` function for standalone execution
- Can be imported and used in other modules
- Follows the existing code style and structure

## Troubleshooting

### Authentication Fails

- Verify your API credentials in `.env`
- Check that your API key has the necessary permissions
- Ensure the API URL is correct for your environment

### Datasets Not Found

- Verify your organization and space settings
- Check that your API credentials have access to the specified organization/space
- Ensure datasets exist in the cloud.gov environment

### Release Fails

- Check that the dataset ID is correct
- Verify the dataset is in a state that allows release
- Review the error messages for specific API responses

## Security Considerations

1. **API Credentials**: Store API keys securely in environment variables, never in code
2. **Metadata**: Be cautious about what information is included in metadata files
3. **Logging**: Avoid logging sensitive information like API keys or secrets
4. **Access Control**: Ensure proper access controls are configured in cloud.gov

## Future Enhancements

Potential improvements for future versions:

- Add support for dataset versioning
- Implement retry logic for failed releases
- Add batch release operations with progress tracking
- Support for dataset validation before release
- Integration with S3 storage (similar to existing metrics)
- Webhook support for automated releases

## Contributing

When contributing to the cloud.gov integration:

1. Follow the existing code style (use `ruff` for linting)
2. Update documentation for new features
3. Add error handling for API calls
4. Include examples for new functionality
5. Test with both development and production environments

## Support

For issues related to:

- **Cloud.gov API**: Contact cloud.gov support
- **Data.gov Integration**: Open an issue in this repository
- **General Questions**: Reach out to the Data.gov team

## Related Documentation

- [Cloud.gov Documentation](https://cloud.gov/docs/)
- [Data.gov Main README](../README.md)
- [Metrics Module README](README.md)
