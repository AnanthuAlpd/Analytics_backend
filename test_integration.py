import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

def test(url):
    print(f"Testing {url}...", end=" ")
    try:
        resp = requests.get(url)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("Response:", resp.text[:100])
        else:
            print("Error Response:", resp.text[:100])
    except Exception as e:
        print(f"Error: {e}")

print("--- DIAGNOSTICS (Integrated Backend) ---")
test(f"{BASE_URL}/api/expenses") # Expect 200
test(f"{BASE_URL}/api/summary") # Expect 200
