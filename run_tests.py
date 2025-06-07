#!/usr/bin/env python3
"""
Script to run all tests for the Flask dashboard project.
"""
import sys
import subprocess


def run_tests():
    """Run pytest with coverage reporting."""
    print("Running Flask Dashboard Tests...")
    print("-" * 50)
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",  # Verbose output
        "--cov=.",  # Coverage for current directory
        "--cov-report=term-missing",  # Show missing lines
        "--cov-report=html",  # Generate HTML coverage report
        "tests/"  # Test directory
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("All tests passed!")
        print("Coverage report generated in htmlcov/index.html")
    else:
        print("\n" + "=" * 50)
        print("Some tests failed. Please check the output above.")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())