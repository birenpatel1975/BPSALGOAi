#!/usr/bin/env python3
"""
Simple test script to verify the API endpoints are working correctly
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5050"

def test_market_live():
    """Test the /api/market/live endpoint"""
    print("\n=== Testing /api/market/live ===")
    try:
        response = requests.get(f"{BASE_URL}/api/market/live", timeout=10)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)[:500]}...")
        if data.get('data') and data['data'].get('symbols'):
            print(f"✅ Got {len(data['data']['symbols'])} symbols")
            return True
        else:
            print("❌ No symbols in response")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_market_live_with_symbols():
    """Test the /api/market/live endpoint with specific symbols"""
    print("\n=== Testing /api/market/live?symbols=NIFTY50&symbols=BANKNIFTY ===")
    try:
        response = requests.get(
            f"{BASE_URL}/api/market/live",
            params={'symbols': ['NIFTY50', 'BANKNIFTY']},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)[:500]}...")
        if data.get('data') and data['data'].get('symbols'):
            print(f"✅ Got {len(data['data']['symbols'])} symbols")
            return True
        else:
            print("❌ No symbols in response")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_algo_watchlist():
    """Test the /api/algo/watchlist endpoint"""
    print("\n=== Testing /api/algo/watchlist ===")
    try:
        response = requests.get(f"{BASE_URL}/api/algo/watchlist", timeout=10)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)[:500]}...")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing BPSAlgoAI API Endpoints...")
    print(f"Base URL: {BASE_URL}")
    
    results = {
        "market_live": test_market_live(),
        "market_live_symbols": test_market_live_with_symbols(),
        "algo_watchlist": test_algo_watchlist(),
    }
    
    print("\n=== Summary ===")
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
