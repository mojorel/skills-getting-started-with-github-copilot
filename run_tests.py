#!/usr/bin/env python3
"""
Test runner script for Mergington High School Activities API
"""

import subprocess
import sys

def run_tests():
    """Run the test suite using pytest"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/", "-v", "--tb=short"
        ], cwd=".")
        return result.returncode == 0
    except FileNotFoundError:
        print("Error: pytest not found. Please install with: pip install pytest")
        return False

if __name__ == "__main__":
    print("Running Mergington High School Activities API tests...")
    success = run_tests()
    sys.exit(0 if success else 1)