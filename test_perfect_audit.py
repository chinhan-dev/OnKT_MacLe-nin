import json, re

with open('quiz_data.js', 'r', encoding='utf-8') as f:
    content = f.read()
json_str = content.replace("window.QUIZ_DATA = ", "").rstrip(";")
data = json.loads(json_str)

all_q = []
for tab_key, tab_data in data.items():
    for q in tab_data['questions']:
        opts = {o['label']: o['text'] for o in q['options']}
        correct_lbl = q['correct_option']
        correct_txt = opts[correct_lbl]
        all_q.append({
            'tab': tab_key,
            'id': q['question_id'],
            'q': re.sub(r'^\d+[\.\s]+', '', q['question']).strip(),
            'correct_lbl': correct_lbl,
            'correct_txt': correct_txt,
            'options': q['options'],
            'opts': opts
        })

rules_perfect = [
    {
        'id': 1,
        'title': '1. Đề hỏi về "Hêghen" (Hegel)',
        'check': lambda q: "hêghen" in q['q'].lower() or "hêghen" in " ".join([o['text'].lower() for o in q['options']])
    },
    {
        'id': 2,
        'title': '2. Đề hỏi về "Phoi-ơ-bắc" (L.Feuerbach)',
        'check': lambda q: "phoi" in q['q'].lower() or "feuerbach" in q['q'].lower()
    },
    {
        'id': 3,
        'title': '3. Đề hỏi "Định nghĩa Vật chất của Lênin" / "Phạm trù vật chất"',
        'check': lambda q: ("thực tại khách quan" in q['correct_txt'].lower() or "độc lập với ý thức" in q['correct_txt'].lower() or "tồn tại khách quan" in q['correct_txt'].lower()) and "bổ sung" not in q['q'].lower()
    },
    {
        'id': 4,
        'title': '4. Đề hỏi "V.I. Lênin bổ sung và phát triển Triết học Mác"',
        'check': lambda q: "lênin bổ sung" in q['q'].lower() or "lênin phát triển" in q['q'].lower() or "độc quyền" in q['correct_txt'].lower()
    },
    {
        'id': 5,
        'title': '5. Đề hỏi về "Chủ nghĩa duy vật chất phác"',
        'check': lambda q: "chất phác" in q['q'].lower() or "chất phác" in q['correct_txt'].lower()
    },
    {
        'id': 6,
        'title': '6. Đề hỏi về "Vận động của vật chất"',
        'check': lambda q: "vận động" in q['q'].lower()
    },
    {
        'id': 7,
        'title': '7. Đề hỏi về "Không gian và Thời gian"',
        'check': lambda q: "không gian" in q['q'].lower() or "thời gian" in q['q'].lower()
    },
    {
        'id': 8,
        'title': '8. Đề hỏi "Bản chất & Nguồn gốc của Ý thức"',
        'check': lambda q: "ý thức" in q['q'].lower() and "ý thức xã hội" not in q['q'].lower() and "tồn tại xã hội" not in q['q'].lower()
    },
    {
        'id': 9,
        'title': '9. Đề hỏi vai trò của "Thực tiễn"',
        'check': lambda q: "thực tiễn" in q['q'].lower()
    },
    {
        'id': 10,
        'title': '10. Đề hỏi "3 Phát minh Khoa học Tự nhiên" tiền đề Mác',
        'check': lambda q: "tiền đề" in q['q'].lower() or "khoa học tự nhiên" in q['q'].lower() or "phát minh" in q['q'].lower()
    },
    {
        'id': 11,
        'title': '11. Đề hỏi quan hệ "Quyết định" (Vật chất / Hạ tầng / Kinh tế)',
        'check': lambda q: "quyết định" in q['q'].lower()
    },
    {
        'id': 12,
        'title': '12. Đề hỏi "Phương thức sản xuất"',
        'check': lambda q: "phương thức sản xuất" in q['q'].lower()
    },
    {
        'id': 13,
        'title': '13. Đề hỏi "Lực lượng sản xuất"',
        'check': lambda q: "lực lượng sản xuất" in q['q'].lower()
    },
    {
        'id': 14,
        'title': '14. Đề hỏi "Quần chúng nhân dân"',
        'check': lambda q: "quần chúng" in q['q'].lower() or "nhân dân" in q['q'].lower()
    }
]

print("=== PERFECT AUDIT RESULTS ===")
for r in rules_perfect:
    matched = [item for item in all_q if r['check'](item)]
    print(f"Rule {r['id']}: [{len(matched)} câu] {r['title']}")

