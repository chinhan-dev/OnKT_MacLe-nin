import re

with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace pushCloudKeysDB with robust awaited fetch
new_push_func = """async function pushCloudKeysDB(keysToPush) {
  try {
    // 1. Fetch latest Cloud Keys
    const getRes = await fetch(CLOUD_DB_ENDPOINT, { cache: 'no-store' });
    let cloudKeys = [];
    if (getRes.ok) {
      const json = await getRes.json();
      if (json && json.data && Array.isArray(json.data.keys)) {
        cloudKeys = json.data.keys;
      }
    }

    // 2. Merge provided keys into cloud keys
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

    // 3. PUT update to Cloud DB & MUST AWAIT RESPONSE COMPLETELY
    const putRes = await fetch(CLOUD_DB_ENDPOINT, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'LMS_VIP_KEYS',
        data: { keys: merged, users: getUsersDB() }
      })
    });

    if (putRes.ok) {
      await putRes.json(); // Ensure full body is consumed before proceeding
      console.log('Successfully pushed and confirmed Cloud DB update.');
    }
  } catch (e) {
    console.warn('Failed to push to Cloud DB:', e);
    localStorage.setItem(VIP_KEYS_STORAGE, JSON.stringify(keysToPush));
  }
}"""

pattern = r"async function pushCloudKeysDB\(keysToPush\) \{.*?\n\}"
code = re.sub(pattern, new_push_func.strip(), code, flags=re.DOTALL)

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated pushCloudKeysDB with full response consumption.")

# Update auth.js to add a small network delay before location.reload()
with open('auth.js', 'r', encoding='utf-8') as f:
    acode = f.read()

old_reload_call = """    if (res.success) {
      if (typeof showToast === 'function') showToast(res.msg, 'success'); else alert(res.msg);
      modal.style.display = 'none';
      location.reload();
    }"""

new_reload_call = """    if (res.success) {
      if (typeof showToast === 'function') showToast(res.msg, 'success'); else alert(res.msg);
      modal.style.display = 'none';
      setTimeout(() => { location.reload(); }, 600);
    }"""

acode = acode.replace(old_reload_call, new_reload_call)

with open('auth.js', 'w', encoding='utf-8') as f:
    f.write(acode)

print("Updated auth.js with 600ms grace period before reload.")

