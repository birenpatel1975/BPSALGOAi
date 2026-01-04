"""Test script to check manual symbol addition"""
import requests

# Test 1: Check if API accepts multiple symbols parameter
print("Test 1: Multiple symbols with 'symbols=' format")
url1 = "http://localhost:5050/api/market/live?symbols=RELIANCE&symbols=TCS"
try:
    response = requests.get(url1, timeout=5)
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Success: {data.get('success')}")
    print(f"Symbols count: {len(data.get('data', {}).get('symbols', []))}")
    print(f"Symbols: {[s.get('symbol') for s in data.get('data', {}).get('symbols', [])]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test 2: Single symbol
print("Test 2: Single symbol")
url2 = "http://localhost:5050/api/market/live?symbols=RELIANCE"
try:
    response = requests.get(url2, timeout=5)
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Success: {data.get('success')}")
    print(f"Symbols count: {len(data.get('data', {}).get('symbols', []))}")
    print(f"Symbols: {[s.get('symbol') for s in data.get('data', {}).get('symbols', [])]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test 3: No symbols (default)
print("Test 3: No symbols (should return defaults)")
url3 = "http://localhost:5050/api/market/live"
try:
    response = requests.get(url3, timeout=5)
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Success: {data.get('success')}")
    print(f"Symbols count: {len(data.get('data', {}).get('symbols', []))}")
    print(f"Symbols: {[s.get('symbol') for s in data.get('data', {}).get('symbols', [])]}")
except Exception as e:
    print(f"Error: {e}")
