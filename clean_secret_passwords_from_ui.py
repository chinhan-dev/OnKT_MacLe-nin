import re

# 1. Clean auth.js
with open('auth.js', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('Đăng nhập Admin Quản Lý Mã (chinhanxt)', 'Đăng nhập Admin Quản Lý Mã')
code = code.replace('(chinhanxt)', '')

with open('auth.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Cleaned auth.js UI text.")

# 2. Clean admin.js
with open('admin.js', 'r', encoding='utf-8') as f:
    acode = f.read()

acode = acode.replace('TRANG QUẢN TRỊ ADMIN (CHỈNH AN)', 'TRANG QUẢN TRỊ ADMIN')
acode = acode.replace('(chinhanxt)', '')
acode = acode.replace(' (CHỈNH AN)', '')

with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(acode)

print("Cleaned admin.js UI text.")

