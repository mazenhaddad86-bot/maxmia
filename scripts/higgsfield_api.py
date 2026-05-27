"""Higgsfield API wrapper using API key — checks cost before any job."""
import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HIGGSFIELD_API_KEY")
BASE = "https://api.higgsfield.ai"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

def check_balance():
    r = requests.get(f"{BASE}/balance", headers=HEADERS)
    print(f"Balance: {r.status_code} -> {r.text[:300]}")
    return r

def list_recent_jobs():
    r = requests.get(f"{BASE}/jobs?page=1&per_page=5", headers=HEADERS)
    print(f"Jobs: {r.status_code} -> {r.text[:500]}")
    return r

def list_images():
    r = requests.get(f"{BASE}/media?page=1&per_page=5", headers=HEADERS)
    print(f"Media: {r.status_code} -> {r.text[:500]}")
    return r

def get_endpoints():
    """Try to discover available endpoints."""
    for path in ["/", "/v1", "/openapi.json", "/docs", "/api", "/health"]:
        r = requests.get(f"{BASE}{path}", headers=HEADERS)
        print(f"GET {path}: {r.status_code} → {r.text[:100]}")

if __name__ == "__main__":
    print(f"API_KEY: {API_KEY[:20]}..." if API_KEY else "NO KEY!")
    print()
    check_balance()
    print()
    list_recent_jobs()
    print()
    list_images()
