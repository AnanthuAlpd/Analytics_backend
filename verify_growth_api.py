import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_growth_api(product_id=None):
    url = f"{BASE_URL}/demo-dashboard/product-growth"
    if product_id:
        url += f"?product_id={product_id}"
    
    print(f"Testing: {url}")
    try:
        resp = requests.get(url)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json().get('data', [])
            print("Data Received:")
            print(json.dumps(data, indent=2))
            
            # Check format
            expected_names = {"Historical Growth", "Current Growth"}
            actual_names = {item['name'] for item in data}
            if actual_names == expected_names:
                print("✅ Data format is correct.")
            else:
                print(f"❌ Unexpected data format: {actual_names}")
        else:
            print(f"❌ Error Response: {resp.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print("-" * 30)

if __name__ == "__main__":
    print("--- VERIFYING PRODUCT GROWTH API ---")
    # Test Total Growth (Initial Load)
    test_growth_api()
    
    # Test Individual Product Growth (Filter)
    test_growth_api(product_id=1)
