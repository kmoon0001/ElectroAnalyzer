#!/usr/bin/env python3
"""Detailed error and status check for ElectroAnalyzer."""

import requests
import json
import sys

print("\n" + "="*80)
print("DETAILED SYSTEM ERROR CHECK")
print("="*80 + "\n")

# Check 1: API Health
print("[CHECK 1] API Health Endpoint")
try:
    resp = requests.get("http://127.0.0.1:8001/health/", timeout=5)
    if resp.status_code == 200:
        data = resp.json()
        print(f"  Status: OK (200)")
        print(f"  Response: {json.dumps(data, indent=2)}")
    else:
        print(f"  ERROR: Status {resp.status_code}")
        print(f"  Response: {resp.text}")
except Exception as e:
    print(f"  ERROR: {e}")

# Check 2: Login
print("\n[CHECK 2] Login Endpoint")
try:
    resp = requests.post(
        "http://127.0.0.1:8001/auth/token",
        data={"username": "admin", "password": "admin123"},
        timeout=5
    )
    if resp.status_code == 200:
        data = resp.json()
        token = data.get("access_token")
        print(f"  Status: OK (200)")
        print(f"  Token issued: {token[:30]}...")
        print(f"  Token type: {data.get('token_type')}")
    else:
        print(f"  ERROR: Status {resp.status_code}")
        print(f"  Response: {resp.text}")
except Exception as e:
    print(f"  ERROR: {e}")

# Check 3: Frontend Port
print("\n[CHECK 3] Frontend Port 3001")
try:
    resp = requests.get("http://127.0.0.1:3001", timeout=5)
    if resp.status_code == 200:
        print(f"  Status: OK (200)")
        print(f"  Frontend is responding")
        # Check if it's actually HTML
        if "<html" in resp.text.lower() or "<!doctype" in resp.text.lower():
            print(f"  Content: Valid HTML")
        else:
            print(f"  Content: {resp.text[:100]}...")
    else:
        print(f"  Status: {resp.status_code}")
except Exception as e:
    print(f"  ERROR: {e}")

# Check 4: Database
print("\n[CHECK 4] Database Connection")
try:
    from pathlib import Path
    db_path = Path("compliance.db")
    if db_path.exists():
        size = db_path.stat().st_size / 1024 / 1024
        print(f"  Status: OK")
        print(f"  File: compliance.db")
        print(f"  Size: {size:.2f} MB")
    else:
        print(f"  ERROR: Database file not found")
except Exception as e:
    print(f"  ERROR: {e}")

# Check 5: Configuration
print("\n[CHECK 5] Configuration")
try:
    import yaml
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
        if config.get("use_ai_mocks"):
            print(f"  Status: OK")
            print(f"  AI Mode: Mock (Enabled)")
        else:
            print(f"  Status: WARNING")
            print(f"  AI Mode: Real AI (May be slow)")
except Exception as e:
    print(f"  ERROR: {e}")

# Check 6: Performance
print("\n[CHECK 6] Response Times")
import time
try:
    start = time.time()
    requests.get("http://127.0.0.1:8001/health/", timeout=5)
    elapsed = (time.time() - start) * 1000
    print(f"  Health Check: {elapsed:.1f}ms")
    
    start = time.time()
    requests.post(
        "http://127.0.0.1:8001/auth/token",
        data={"username": "admin", "password": "admin123"},
        timeout=5
    )
    elapsed = (time.time() - start) * 1000
    print(f"  Login: {elapsed:.1f}ms")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "="*80)
print("ERROR CHECK COMPLETE")
print("="*80 + "\n")
