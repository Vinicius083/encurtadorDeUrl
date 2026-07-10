import requests
import json
import uuid

base_url = "http://localhost:8000"

email = f"test_{uuid.uuid4().hex}@test.com"
user_payload = {
    "nome": "Test User",
    "email": email,
    "senha": "password123"
}
resp = requests.post(f"{base_url}/register", json=user_payload)
token = resp.json().get("token")
headers = {"Authorization": f"Bearer {token}"}

url_payload = {
    "url_original": "https://www.google.com"
}
resp = requests.post(f"{base_url}/url", json=url_payload, headers=headers)
codigo = resp.json().get("codigo")
print(f"Created URL code: {codigo}")

print("Testing 49 accesses...")
for i in range(49):
    resp = requests.get(f"{base_url}/u/{codigo}", allow_redirects=False)
    assert resp.status_code == 307
print("Reached 49 accesses.")

# Access 50th time
resp = requests.get(f"{base_url}/u/{codigo}", allow_redirects=False)
assert resp.status_code == 307
print("50 accesses. Should be cached now.")

# Access 51st time (should hit cache)
resp = requests.get(f"{base_url}/u/{codigo}", allow_redirects=False)
assert resp.status_code == 307
print("51 accesses. Hit cache!")
print("Checking Redis directly to confirm...")
