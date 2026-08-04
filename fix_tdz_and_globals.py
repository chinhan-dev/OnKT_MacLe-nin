with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Make sure all constants are at the absolute top of the file
top_constants = """/* ==========================================================================
   GLOBAL CONSTANTS & CONFIGURATION
   ========================================================================== */
const ADMIN_PASS = 'chinhanxt';
const VIP_KEYS_STORAGE = 'lms_vip_keys_db';
const USERS_DB_STORAGE = 'lms_users_db';
const DEVICE_ID_KEY = 'lms_device_fingerprint';
const ACTIVATED_KEY_STORAGE = 'lms_activated_vip_key';
const CLOUD_DB_ENDPOINT = 'https://jsonblob.com/api/jsonBlob/019fcb1f-708b-750f-948f-caa9398416e8';

"""

# Remove duplicated const declarations
code = code.replace("const CLOUD_DB_ENDPOINT = 'https://jsonblob.com/api/jsonBlob/019fcb1f-708b-750f-948f-caa9398416e8';", "")
code = code.replace("const ADMIN_PASS = 'chinhanxt';", "")
code = code.replace("const VIP_KEYS_STORAGE = 'lms_vip_keys_db';", "")
code = code.replace("const USERS_DB_STORAGE = 'lms_users_db';", "")
code = code.replace("const DEVICE_ID_KEY = 'lms_device_fingerprint';", "")
code = code.replace("const ACTIVATED_KEY_STORAGE = 'lms_activated_vip_key';", "")

# Ensure fetchCloudKeysDB is explicitly declared globally
fetch_keys_alias = """
async function fetchCloudKeysDB() {
  const d = await fetchCloudData();
  return d.keys;
}

async function pushCloudKeysDB(keysToPush) {
  await pushCloudData(keysToPush, getUsersDB());
}
"""

if "async function fetchCloudKeysDB" not in code:
    code = code + "\n" + fetch_keys_alias

# Put top constants at the front
code = top_constants + code.strip()

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Re-ordered admin.js to eliminate Temporal Dead Zone (TDZ) and missing globals.")
