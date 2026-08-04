import re

# 1. Update index.html toggle text to be short & compact
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('Chế độ Ôn Luyện (Ẩn đáp án)', 'Ôn Luyện (Ẩn đáp án)')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html toggle text.")

# 2. Add header element polish CSS to styles.css
header_element_css = """

/* High-End Header Compact Polish */
.brand-text h1 {
  font-size: 1.1rem !important;
  font-weight: 800;
  white-space: nowrap !important;
}

.brand-text p {
  font-size: 0.72rem !important;
  color: var(--text-muted);
  white-space: nowrap !important;
}

.toggle-wrapper {
  padding: 4px 10px !important;
  border-radius: 9999px;
  gap: 8px !important;
  white-space: nowrap !important;
}

.toggle-label {
  font-size: 0.8rem !important;
  white-space: nowrap !important;
}

.switch {
  width: 36px !important;
  height: 20px !important;
}

.slider:before {
  height: 14px !important;
  width: 14px !important;
  left: 3px !important;
  bottom: 3px !important;
}

input:checked + .slider:before {
  transform: translateX(16px) !important;
}

/* VIBRANT HIGH-CONTRAST MẸO HỌC BUTTON */
.btn-meohoc-header {
  white-space: nowrap !important;
  display: inline-flex !align-items: center;
  align-items: center;
  gap: 6px;
  padding: 6px 14px !important;
  border-radius: 9999px !important;
  background: linear-gradient(135deg, #db2777, #7c3aed) !important;
  color: #ffffff !important;
  font-weight: 800 !important;
  font-size: 0.85rem !important;
  text-decoration: none;
  box-shadow: 0 4px 14px rgba(219, 39, 119, 0.4) !important;
  transition: all 0.2s ease !important;
}

.btn-meohoc-header i {
  color: #fbbf24 !important; /* Glowing golden bulb icon */
  font-size: 0.95rem;
}

.btn-meohoc-header:hover {
  transform: translateY(-2px) scale(1.03) !important;
  box-shadow: 0 6px 18px rgba(219, 39, 119, 0.6) !important;
}

/* Compact Reset Button */
.btn-reset-header {
  white-space: nowrap !important;
  padding: 6px 12px !important;
  font-size: 0.8rem !important;
}
"""

with open('styles.css', 'a', encoding='utf-8') as f:
    f.write(header_element_css)

print("Header element polish CSS added to styles.css.")

