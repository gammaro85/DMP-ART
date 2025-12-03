#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for verifying DMP-ART standalone build

Usage:
    python test_build.py [path_to_dist_folder]

Example:
    python test_build.py dist/DMP-ART
"""

import os
import sys
import json
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")

def test_result(passed, message):
    if passed:
        print(f"{Colors.GREEN}✓ PASS:{Colors.END} {message}")
        return True
    else:
        print(f"{Colors.RED}✗ FAIL:{Colors.END} {message}")
        return False

def test_folder_structure(dist_path):
    """Test if all required folders exist."""
    print_header("Testing Folder Structure")

    required_folders = [
        'input',
        'output',
        'output/dmp',
        'output/reviews',
        'output/cache',
        'config',
        '_internal',  # PyInstaller runtime
    ]

    passed = 0
    failed = 0

    for folder in required_folders:
        folder_path = dist_path / folder
        if test_result(folder_path.exists(), f"Folder exists: {folder}"):
            passed += 1
        else:
            failed += 1

    return passed, failed

def test_executable_exists(dist_path):
    """Test if executable file exists."""
    print_header("Testing Executable")

    # Different executable names for different platforms
    possible_executables = [
        'DMP-ART.exe',  # Windows
        'DMP-ART',       # Linux/Mac
    ]

    for exe_name in possible_executables:
        exe_path = dist_path / exe_name
        if exe_path.exists():
            test_result(True, f"Executable found: {exe_name}")

            # Check if it's executable (Unix)
            if exe_name != 'DMP-ART.exe':
                is_executable = os.access(exe_path, os.X_OK)
                test_result(is_executable, f"Has execute permissions")

            return 1, 0

    test_result(False, "No executable found")
    return 0, 1

def test_config_files(dist_path):
    """Test if config files exist and are valid JSON."""
    print_header("Testing Config Files")

    config_files = [
        'config/dmp_structure.json',
        'config/quick_comments.json',
        'config/newcomer.json',
        'config/mising.json',
        'config/ready.json',
    ]

    passed = 0
    failed = 0

    for config_file in config_files:
        config_path = dist_path / config_file

        # Test existence
        if not test_result(config_path.exists(), f"File exists: {config_file}"):
            failed += 1
            continue

        # Test if valid JSON
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                json.load(f)
            test_result(True, f"Valid JSON: {config_file}")
            passed += 1
        except json.JSONDecodeError as e:
            test_result(False, f"Invalid JSON: {config_file} - {str(e)}")
            failed += 1

    return passed, failed

def test_documentation(dist_path):
    """Test if documentation files exist."""
    print_header("Testing Documentation")

    doc_files = [
        'INSTRUKCJA.txt',
        'input/README.txt',
        'output/README.txt',
    ]

    passed = 0
    failed = 0

    for doc_file in doc_files:
        doc_path = dist_path / doc_file
        if test_result(doc_path.exists(), f"Documentation: {doc_file}"):
            passed += 1

            # Check if not empty
            if doc_path.stat().st_size > 0:
                test_result(True, f"  → Not empty ({doc_path.stat().st_size} bytes)")
            else:
                test_result(False, f"  → Empty file!")
                failed += 1
        else:
            failed += 1

    return passed, failed

def test_internal_structure(dist_path):
    """Test if PyInstaller internal structure is correct."""
    print_header("Testing Internal Structure")

    internal_path = dist_path / '_internal'

    passed = 0
    failed = 0

    # Test if _internal folder exists
    if test_result(internal_path.exists(), "PyInstaller _internal folder"):
        passed += 1

        # Test critical folders
        critical_folders = [
            '_internal/templates',
            '_internal/static',
            '_internal/utils',
        ]

        for folder in critical_folders:
            folder_path = dist_path / folder
            if test_result(folder_path.exists(), f"  → {folder}"):
                passed += 1
            else:
                failed += 1
    else:
        failed += 1

    return passed, failed

def test_file_permissions(dist_path):
    """Test if files have correct permissions."""
    print_header("Testing File Permissions")

    # Skip on Windows
    if sys.platform == 'win32':
        print(f"{Colors.YELLOW}⊘ SKIP: File permissions test (Windows){Colors.END}")
        return 0, 0

    passed = 0
    failed = 0

    # Executable should have execute permission
    exe_path = dist_path / 'DMP-ART'
    if exe_path.exists():
        is_executable = os.access(exe_path, os.X_OK)
        if test_result(is_executable, "Executable has +x permission"):
            passed += 1
        else:
            failed += 1

    return passed, failed

def calculate_total_size(dist_path):
    """Calculate total size of distribution."""
    total_size = 0
    for root, dirs, files in os.walk(dist_path):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)

    # Convert to MB
    size_mb = total_size / (1024 * 1024)
    return size_mb

def print_summary(total_passed, total_failed, dist_path):
    """Print final summary."""
    print_header("Test Summary")

    total_tests = total_passed + total_failed
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print(f"Total tests:  {total_tests}")
    print(f"{Colors.GREEN}Passed:       {total_passed} ({success_rate:.1f}%){Colors.END}")

    if total_failed > 0:
        print(f"{Colors.RED}Failed:       {total_failed}{Colors.END}")
    else:
        print(f"Failed:       {total_failed}")

    # Distribution size
    size_mb = calculate_total_size(dist_path)
    print(f"\nDistribution size: {size_mb:.1f} MB")

    # Size warning
    if size_mb > 200:
        print(f"{Colors.YELLOW}⚠ Warning: Distribution is quite large (>{size_mb:.0f} MB){Colors.END}")

    # Final result
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    if total_failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED - BUILD IS VALID{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED - BUILD NEEDS FIXING{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

    return total_failed == 0

def main():
    """Main test runner."""
    # Parse arguments
    if len(sys.argv) > 1:
        dist_path = Path(sys.argv[1])
    else:
        dist_path = Path('dist/DMP-ART')

    # Check if path exists
    if not dist_path.exists():
        print(f"{Colors.RED}Error: Distribution folder not found: {dist_path}{Colors.END}")
        print(f"\nUsage: python test_build.py [path_to_dist_folder]")
        print(f"Example: python test_build.py dist/DMP-ART")
        sys.exit(1)

    print(f"\n{Colors.BOLD}Testing distribution at: {dist_path.absolute()}{Colors.END}")

    # Run all tests
    total_passed = 0
    total_failed = 0

    tests = [
        test_folder_structure,
        test_executable_exists,
        test_config_files,
        test_documentation,
        test_internal_structure,
        test_file_permissions,
    ]

    for test_func in tests:
        passed, failed = test_func(dist_path)
        total_passed += passed
        total_failed += failed

    # Print summary
    success = print_summary(total_passed, total_failed, dist_path)

    # Exit code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}CRITICAL ERROR: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
