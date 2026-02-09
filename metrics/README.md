# datagov-metrics

A python module to fetch metrics from various sources (GA & CKAN) and push them to S3

Reports are then available at the path:

https://s3-us-gov-west-1.amazonaws.com/cg-baa85e06-1bdd-4672-9e3a-36333c05c6ce/{file_name}

Ex.
https://s3-us-gov-west-1.amazonaws.com/cg-baa85e06-1bdd-4672-9e3a-36333c05c6ce/global__datasets_per_org.csv

## Cloud.gov Integration

This module also includes integration with cloud.gov for dataset management and release.

See the [Cloud.gov Integration Guide](../docs/cloudgov-integration.md) for detailed documentation.

### Quick Start

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your cloud.gov credentials

3. Run the dataset release script:
   ```bash
   python release_datasets.py --help
   ```

### Testing

To run tests for the cloud.gov module:

```bash
poetry install
poetry run python -m unittest test_cloudgov.py -v
```

