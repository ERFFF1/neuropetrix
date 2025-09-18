#!/usr/bin/env python3
"""
Test Runner
Test çalıştırıcı script
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {description}")
        print(f"Command: {command}")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="NeuroPETRIX Test Runner")
    parser.add_argument("--type", choices=["unit", "integration", "e2e", "all"], default="all",
                       help="Type of tests to run")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--parallel", "-n", type=int, help="Run tests in parallel")
    parser.add_argument("--markers", help="Run tests with specific markers")
    
    args = parser.parse_args()
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🧪 NeuroPETRIX Test Suite")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🎯 Test type: {args.type}")
    
    # Base pytest command
    base_cmd = "python -m pytest"
    
    # Add coverage if requested
    if args.coverage:
        base_cmd += " --cov=backend --cov-report=html --cov-report=term"
    
    # Add verbose if requested
    if args.verbose:
        base_cmd += " -v"
    
    # Add parallel execution if requested
    if args.parallel:
        base_cmd += f" -n {args.parallel}"
    
    # Add markers if specified
    if args.markers:
        base_cmd += f" -m {args.markers}"
    
    # Determine which tests to run
    if args.type == "unit":
        cmd = f"{base_cmd} tests/test_unit.py -m unit"
    elif args.type == "integration":
        cmd = f"{base_cmd} tests/test_integration.py -m integration"
    elif args.type == "e2e":
        cmd = f"{base_cmd} tests/test_e2e.py -m e2e"
    else:  # all
        cmd = f"{base_cmd} tests/"
    
    # Run the tests
    success = run_command(cmd, f"Running {args.type} tests")
    
    if success:
        print(f"\n✅ {args.type.title()} tests completed successfully!")
        
        if args.coverage:
            print("\n📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n❌ {args.type.title()} tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
