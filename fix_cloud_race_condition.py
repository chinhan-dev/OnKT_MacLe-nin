import re

with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

new_cloud_logic = """
const CLOUD_DB_ENDPOINT = 'https://api.restful-api.dev/objects/ff8081819f7e10ae019fcafb3a556dde';

// Fetch Keys from Cloud DB & Merge cleanly
async function fetchCloudKeysDB() {
  try {
    const res = await fetch(CLOUD_DB_ENDPOINT);
    if (res.ok) {
      const json = await res.json();
      if (json && json.data && Array.isArray(json.data.keys)) {
        const cloudKeys = json.data.keys;
        const localData = localStorage.getItem(VIP_KEYS_STORAGE);
        let localKeys = localData ? JSON.parse(localData) : [];

        // Merge: keep all Cloud keys, plus any unique local keys
        const mergedKeys = [...cloudKeys];
        for (const lk of localKeys) {
          if (!mergedKeys.some(ck => ck.key.toUpperCase() === lk.key.toUpperCase())) {
            mergedKeys.push(lk);
          }
        }

        localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(mergedKeys));
        return mergedKeys;
      }
    }
  } catch (e) {
    console.warn('Cloud DB fetch offline, falling back to local storage.', e);
  }
  return getVipKeysDB();
}

// Push Keys to Cloud DB safely with Merge
async function pushCloudKeysDB(keysToPush) {
  try {
    const res = await fetch(CLOUD_DB_ENDPOINT);
    let cloudKeys = [];
    if (res.ok) {
      const json = await res.json();
      if (json && json.data && Array.isArray(json.data.keys)) {
        cloudKeys = json.data.keys;
      }
    }

    const merged = [...cloudKeys];
    for (const k of keysToPush) {
      const idx = merged.findIndex(ck => ck.key.toUpperCase() === k.key.toUpperCase());
      if (idx >= 0) {
        merged[idx] = k;
      } else {
        merged.push(k);
      }
    }

    localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(merged));

    await fetch(CLOUD_DB_ENDPOINT, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'LMS_VIP_KEYS',
        data: { keys: merged, users: getUsersDB() }
      })
    });
  } catch (e) {
    console.warn('Failed to push to Cloud DB:', e);
    localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(keysToPush));
  }
}
"""

pattern = r"const CLOUD_DB_ENDPOINT = .*?async function pushCloudKeysDB\(keys\) \{.*?\n\}"
code = re.sub(pattern, new_cloud_logic.strip(), code, flags=re.DOTALL)

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed Cloud DB race condition in admin.js.")
