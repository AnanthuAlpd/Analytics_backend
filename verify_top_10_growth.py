import urllib.request
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_top_10_growth():
    url = f"{BASE_URL}/demo-dashboard/top-10-product-growth"
    print(f"Testing: {url}")
    try:
        with urllib.request.urlopen(url) as response:
            status_code = response.getcode()
            print(f"Status Code: {status_code}")
            
            if status_code == 200:
                data_bytes = response.read()
                data_json = json.loads(data_bytes)
                data = data_json.get('data', [])
                print(f"Data Count: {len(data)}")
                
                if len(data) > 0:
                    print("First Item Sample:")
                    print(json.dumps(data[0], indent=2))
                    
                    # Verify structure
                    first_item = data[0]
                    if 'name' in first_item and 'series' in first_item:
                        series = first_item['series']
                        if len(series) == 2:
                             names = {s['name'] for s in series}
                             if names == {"Current Growth", "Predicted Growth"}:
                                 print("✅ Structure is correct (name + series[Current, Predicted])")
                             else:
                                 print(f"❌ Unexpected series names: {names}")
                        else:
                             print(f"❌ Series length mismatch: {len(series)}")
                    else:
                        print("❌ Dictionary keys mismatch")
                    
                    def get_growth(item):
                        for s in item['series']:
                            if s['name'] == 'Current Growth':
                                return s['value']
                        return -999999

                    first_growth = get_growth(data[0])
                    last_growth = get_growth(data[-1])
                    
                    print(f"First Item Growth: {first_growth}")
                    print(f"Last Item Growth: {last_growth}")
                    
                    if first_growth >= last_growth:
                         print("✅ Sorting appears correct (Descending)")
                    else:
                         print("❌ Sorting might be wrong")

                else:
                    print("⚠️ No data returned (might be empty DB?)")

            else:
                 print(f"❌ Error Response: {status_code}")

    except Exception as e:
        print(f"❌ Exception: {e}")
    print("-" * 30)

if __name__ == "__main__":
    test_top_10_growth()
