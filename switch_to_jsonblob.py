with open('admin.js', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    "const CLOUD_DB_ENDPOINT = 'https://api.restful-api.dev/objects/ff8081819f7e10ae019fcafb3a556dde';",
    "const CLOUD_DB_ENDPOINT = 'https://jsonblob.com/api/jsonBlob/019fcb1f-708b-750f-948f-caa9398416e8';"
)

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Switched CLOUD_DB_ENDPOINT to jsonblob.com.")
