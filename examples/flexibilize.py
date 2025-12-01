#!/usr/bin/env python3
"""
Example: Flexibilize a DECOMP execution.

Usage:
    python flexibilize.py <bucket> <execution_hash>

Environment:
    FLEXIBILIZADOR_URL - Service base URL (default: http://localhost:8000)

Examples:
    python flexibilize.py decomp-bucket abc123def456
    FLEXIBILIZADOR_URL=http://api.example.com python flexibilize.py my-bucket hash123
"""

import json
import os
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)


BASE_URL = os.environ.get("FLEXIBILIZADOR_URL", "http://localhost:8000")


def check_health() -> bool:
    """Check if the service is healthy."""
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=10)
        return response.status_code == 200
    except httpx.RequestError as e:
        print(f"Connection error: {e}")
        return False


def flexibilize(
    bucket: str, execution_hash: str, program: str = "DECOMP"
) -> dict:
    """
    Apply flexibilization to a DECOMP execution.

    Args:
        bucket: S3 bucket containing artifacts
        execution_hash: Execution identifier
        program: Program type (default: DECOMP)

    Returns:
        Flexibilization response

    Raises:
        SystemExit: On API error
    """
    response = httpx.post(
        f"{BASE_URL}/flex/",
        json={
            "bucket": bucket,
            "execution_hash": execution_hash,
            "program": program,
            "output_prefix": "ingest",
        },
        timeout=120,
    )

    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}")
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2))
        except json.JSONDecodeError:
            print(response.text)
        sys.exit(1)

    return response.json()


def print_results(result: dict) -> None:
    """Print flexibilization results in a readable format."""
    print(f"\n{'=' * 60}")
    print("FLEXIBILIZATION RESULTS")
    print(f"{'=' * 60}")
    print(f"Success:   {result['success']}")
    print(f"Hash:      {result['execution_hash']}")
    print(f"Output:    {result['output_key']}")
    print(f"Message:   {result.get('message', 'N/A')}")

    flexibilizations = result.get("flexibilizations", [])
    print(f"\nFlexibilizations Applied: {len(flexibilizations)}")

    if flexibilizations:
        print(f"\n{'-' * 60}")
        for i, flex in enumerate(flexibilizations, 1):
            print(f"\n[{i}] {flex.get('type', 'Unknown')}")
            if flex.get("target"):
                print(f"    Target: {flex['target']}")
            if flex.get("original_value") is not None:
                print(f"    Original: {flex['original_value']}")
            if flex.get("new_value") is not None:
                print(f"    New: {flex['new_value']}")
            if flex.get("reason"):
                print(f"    Reason: {flex['reason']}")

    print(f"\n{'=' * 60}\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    bucket = sys.argv[1]
    execution_hash = sys.argv[2]
    program = sys.argv[3] if len(sys.argv) > 3 else "DECOMP"

    print(f"Service URL: {BASE_URL}")
    print(f"Bucket:      {bucket}")
    print(f"Hash:        {execution_hash}")
    print(f"Program:     {program}")

    # Health check
    print("\nChecking service health...")
    if not check_health():
        print("Service is not available")
        sys.exit(1)
    print("Service is healthy ✓")

    # Flexibilize
    print(f"\nFlexibilizing {execution_hash}...")
    result = flexibilize(bucket, execution_hash, program)

    # Print results
    print_results(result)


if __name__ == "__main__":
    main()
