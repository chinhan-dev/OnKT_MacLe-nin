import json, re

# 1. Link styles.css in meo_hoc.html
with open('meo_hoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

if 'styles.css' not in html:
    html = html.replace('</head>', '  <link rel="stylesheet" href="styles.css">\n</head>')
    with open('meo_hoc.html', 'w', encoding='utf-8') as f:
        f.write(html)

print("Linked styles.css in meo_hoc.html.")

# 2. Also update generate_interactive_meo_hoc.py so future regenerations include styles.css
with open('generate_interactive_meo_hoc.py', 'r', encoding='utf-8') as f:
    code = f.read()

if 'styles.css' not in code:
    code = code.replace('</head>', '  <link rel="stylesheet" href="styles.css">\n</head>')
    with open('generate_interactive_meo_hoc.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Updated generate_interactive_meo_hoc.py with styles.css link.")

