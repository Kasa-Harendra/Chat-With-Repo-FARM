import requests
import time

BASE_URL = "http://localhost:8000/api/repo"

def test_status_loop():
    # Note: In a real test we'd need a valid session cookie
    # This check is just to see if the endpoint exists and returns 400 when no session is found
    try:
        response = requests.get(f"{BASE_URL}/status")
        print(f"Status check without session: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_status_loop()
