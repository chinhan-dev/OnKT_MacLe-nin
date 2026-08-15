import random
import string
import requests
import json

def gen_code():
    chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"MAC-{chars}"

key1 = gen_code()
key2 = gen_code()

created_at = "4/8/2026 12:12:00"

clean_db = {
    "keys": [
        {
            "key": key1,
            "status": "unused",
            "deviceId": None,
            "createdAt": created_at
        },
        {
            "key": key2,
            "status": "unused",
            "deviceId": None,
            "createdAt": created_at
        }
    ],
    "users": []
}

url = "https://jsonblob.com/api/jsonBlob/019fcb1f-708b-750f-948f-caa9398416e8"
headers = {"Content-Type": "application/json"}

res = requests.put(url, headers=headers, json=clean_db)
print("HTTP Status:", res.status_code)
print("Clean DB Body:", json.dumps(res.json(), indent=2, ensure_ascii=False))

