import requests

BASE_URL = "http://localhost:8000/api"

print("=" * 60)
print("TESTING PHOTO URLs IN API RESPONSE")
print("=" * 60)

# Login as supervisor
login_response = requests.post(f"{BASE_URL}/auth/login/", json={
    "username": "admin",
    "password": "admin123"
})

if login_response.status_code == 200:
    token = login_response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get submission detail
    response = requests.get(f"{BASE_URL}/supervisor/submissions/1", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        submission = data['submission']
        
        print(f"\nSubmission ID: {submission['id']}")
        print(f"Total Photos: {len(submission['photos'])}")
        
        print("\nPhoto URLs (first 3):")
        for photo in submission['photos'][:3]:
            print(f"  Section {photo['section']}, Order {photo['order_index']}")
            print(f"  URL: {photo['file_url']}")
            print(f"  Full URL: http://localhost:8000/media/{photo['file_url']}")
            
            # Test if photo is accessible
            photo_url = f"http://localhost:8000/media/{photo['file_url']}"
            photo_response = requests.get(photo_url)
            print(f"  Accessible: {photo_response.status_code == 200}")
            print()
    else:
        print(f"Failed to get submission: {response.status_code}")
else:
    print(f"Login failed: {login_response.status_code}")

print("=" * 60)
