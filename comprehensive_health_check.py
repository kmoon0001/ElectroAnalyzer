#!/usr/bin/env python3
"""Comprehensive health check for ElectroAnalyzer application."""

import subprocess
import requests
import time
import sys
import os
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_check(status, message, details=""):
    symbol = "[OK]" if status else "[FAIL]"
    color = "\033[92m" if status else "\033[91m"  # Green or Red
    reset = "\033[0m"
    print(f"{symbol} {message}")
    if details:
        print(f"  -> {details}")

def check_api_server():
    """Check API server health."""
    print_header("1. API SERVER CHECK")
    try:
        time.sleep(5)  # Wait for server to start
        response = requests.get("http://127.0.0.1:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_check(True, "API Server is RUNNING", f"Status: {data.get('status')}")
            print_check(True, "AI Mode", f"Mode: {data.get('checks', {}).get('ai_models', {}).get('status', 'unknown')}")
            print_check(True, "Uptime", f"Uptime: {data.get('uptime_seconds', 0):.1f}s")
            return True
        else:
            print_check(False, f"API Server returned status {response.status_code}")
            return False
    except Exception as e:
        print_check(False, "API Server is NOT RESPONDING", str(e))
        return False

def check_database():
    """Check database connection."""
    print_header("2. DATABASE CHECK")
    try:
        db_path = Path("compliance.db")
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print_check(True, "Database file exists", f"Size: {size_mb:.2f} MB")
        else:
            print_check(False, "Database file not found")
            return False

        # Check if database is accessible
        response = requests.post(
            "http://127.0.0.1:8001/auth/token",
            data={"username": "admin", "password": "admin123"},
            timeout=5
        )
        if response.status_code == 200:
            print_check(True, "Database connection is working", "Login endpoint accessible")
            return True
        else:
            print_check(False, f"Database check failed with status {response.status_code}")
            return False
    except Exception as e:
        print_check(False, "Database check failed", str(e))
        return False

def check_authentication():
    """Check authentication system."""
    print_header("3. AUTHENTICATION CHECK")
    try:
        response = requests.post(
            "http://127.0.0.1:8001/auth/token",
            data={"username": "admin", "password": "admin123"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print_check(True, "Admin user can authenticate", f"Token received: {token[:20]}...")
            print_check(True, "Token type", f"Type: {data.get('token_type')}")
            return True
        else:
            print_check(False, f"Authentication failed with status {response.status_code}")
            return False
    except Exception as e:
        print_check(False, "Authentication check failed", str(e))
        return False

def check_frontend_dependencies():
    """Check if frontend dependencies are installed."""
    print_header("4. FRONTEND DEPENDENCIES CHECK")
    try:
        frontend_dir = Path("frontend/electron-react-app")
        node_modules = frontend_dir / "node_modules"
        package_json = frontend_dir / "package.json"

        if package_json.exists():
            print_check(True, "package.json found")
        else:
            print_check(False, "package.json not found")
            return False

        if node_modules.exists() and list(node_modules.iterdir()):
            num_packages = len(list(node_modules.iterdir()))
            print_check(True, "npm dependencies installed", f"Packages: {num_packages}")
            return True
        else:
            print_check(False, "npm dependencies not installed", "Run: npm install --legacy-peer-deps")
            return False
    except Exception as e:
        print_check(False, "Frontend check failed", str(e))
        return False

def check_configuration():
    """Check configuration files."""
    print_header("5. CONFIGURATION CHECK")
    try:
        config_yaml = Path("config.yaml")
        if config_yaml.exists():
            with open(config_yaml, 'r') as f:
                content = f.read()
                if "use_ai_mocks: true" in content:
                    print_check(True, "AI mocks enabled", "Config: use_ai_mocks: true")
                else:
                    print_check(False, "AI mocks not enabled")
                    return False
        else:
            print_check(False, "config.yaml not found")
            return False

        env_file = Path(".env")
        if env_file.exists():
            print_check(True, ".env file exists")
        else:
            print_check(True, ".env file not needed (using defaults)")

        return True
    except Exception as e:
        print_check(False, "Configuration check failed", str(e))
        return False

def check_api_endpoints():
    """Check critical API endpoints."""
    print_header("6. API ENDPOINTS CHECK")

    endpoints = [
        ("GET", "/docs", "API Documentation"),
        ("GET", "/api/v2/system/health", "System Health"),
    ]

    results = []
    for method, endpoint, name in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"http://127.0.0.1:8001{endpoint}", timeout=5)
            status = response.status_code == 200
            results.append(status)
            print_check(status, f"{name} ({endpoint})", f"Status: {response.status_code}")
        except Exception as e:
            results.append(False)
            print_check(False, f"{name} ({endpoint})", str(e))

    return all(results)

def main():
    """Run all health checks."""
    print("\n" + "="*60)
    print("  ELECTROANALYZER - COMPREHENSIVE HEALTH CHECK")
    print("="*60)

    results = {
        "API Server": check_api_server(),
        "Database": check_database(),
        "Authentication": check_authentication(),
        "Frontend Dependencies": check_frontend_dependencies(),
        "Configuration": check_configuration(),
        "API Endpoints": check_api_endpoints(),
    }

    # Summary
    print_header("SUMMARY")
    total = len(results)
    passed = sum(results.values())

    for component, status in results.items():
        symbol = "[OK]" if status else "[FAIL]"
        color = "\033[92m" if status else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{symbol}{reset} {component}: {'PASS' if status else 'FAIL'}")

    print(f"\nTotal: {passed}/{total} checks passed")

    if passed == total:
        print("\n[OK] All systems operational! Application is ready to use.")
        print("\nNext steps:")
        print("1. Frontend: http://127.0.0.1:3001")
        print("2. Login: admin / admin123")
        print("3. Upload documents to analyze")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} components need attention. See details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
