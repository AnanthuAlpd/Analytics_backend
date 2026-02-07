import requests
import json

BASE_URL = "http://localhost:5000/api"

def get_summary():
    try:
        resp = requests.get(f"{BASE_URL}/summary")
        if resp.status_code == 200:
            return resp.json()
        print(f"Failed to get summary: {resp.text}")
        return None
    except Exception as e:
        print(f"Error getting summary: {e}")
        return None

def add_expense(amount, type_val):
    data = {
        "description": "Debug Test",
        "amount": amount,
        "type": type_val,
        "category": "Debug",
        "date": "2026-02-05T12:00:00"
    }
    try:
        resp = requests.post(f"{BASE_URL}/expenses", json=data)
        if resp.status_code == 201:
            print(f"Added {type_val} of {amount}")
            return resp.json()['id']
        print(f"Failed to add expense: {resp.text}")
        return None
    except Exception as e:
        print(f"Error adding expense: {e}")
        return None

def delete_expense(id):
    requests.delete(f"{BASE_URL}/expenses/{id}")
    print(f"Deleted expense {id}")

print("--- INITIAL SUMMARY ---")
s1 = get_summary()
print(json.dumps(s1, indent=2))

if s1:
    print("\n--- ADDING INCOME (1000) ---")
    id1 = add_expense(1000, "income")
    
    print("\n--- ADDING EXPENSE (500) ---")
    id2 = add_expense(500, "expense")
    
    print("\n--- NEW SUMMARY ---")
    s2 = get_summary()
    print(json.dumps(s2, indent=2))
    
    # Verification
    if s2:
        expected_income = s1['total_income'] + 1000
        expected_expense = s1['total_expense'] + 500
        
        print(f"\nExpected Income: {expected_income} | Actual: {s2['total_income']}")
        print(f"Expected Expense: {expected_expense} | Actual: {s2['total_expense']}")
        
        if s2['total_income'] == expected_income and s2['total_expense'] == expected_expense:
            print("✅ BACKEND UPDATE WORKS CORRECTLY")
        else:
            print("❌ BACKEND UPDATE FAILED")

    # Cleanup
    if id1: delete_expense(id1)
    if id2: delete_expense(id2)
