import json, re
from collections import defaultdict

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
            'q': q['question'],
            'correct_lbl': correct_lbl,
            'correct_txt': correct_txt,
            'opts': opts
        })

print(f"Total Questions Analyzed: {len(all_q)}")

# Loopholes Rules mapping
loopholes = [
    {
        'rule': 'Dấu hiệu "Hêghen" -> Chọn "Duy tâm khách quan" hoặc "Phép biện chứng"',
        'check_q': lambda q: "hêghen" in q.lower(),
        'matched': []
    },
    {
        'rule': 'Dấu hiệu "Phoi-ơ-bắc / Feuerbach" -> Chọn "Duy vật siêu hình" hoặc "Duy vật chất phác"',
        'check_q': lambda q: "phoi" in q.lower() or "feuerbach" in q.lower(),
        'matched': []
    },
    {
        'rule': 'Dấu hiệu "Lênin" / "Vật chất" -> Chọn "Thực tại khách quan"',
        'check_q': lambda q: "lênin" in q.lower() or "vật chất là" in q.lower() or "định nghĩa vật chất" in q.lower(),
        'matched': []
    },
    {
        'rule': 'Dấu hiệu "Vận động" -> Chọn "Phương thức tồn tại của vật chất"',
        'check_q': lambda q: "vận động" in q.lower(),
        'matched': []
    },
    {
        'rule': 'Dấu hiệu "Không gian" / "Thời gian" -> Chọn "Hình thức tồn tại của vật chất"',
        'check_q': lambda q: "không gian" in q.lower() or "thời gian" in q.lower(),
        'matched': []
    },
    {
        'rule': 'Dấu hiệu "Ý thức" -> Chọn "Bản chất là hình ảnh phản ánh tích cực, sáng tạo"',
        'check_q': lambda q: "ý thức" in q.lower() and "nguồn gốc" not in q.lower(),
        'matched': []
    },
    {
        'rule': 'Dấu hiệu "Thực tiễn" -> Chọn "Cơ sở, động lực, mục đích của nhận thức"',
        'check_q': lambda q: "thực tiễn" in q.lower(),
        'matched': []
    },
    {
        'rule': 'Dấu hiệu "Tiền đề KHTN" / "Phát minh" -> Chọn "Tế bào / Năng lượng / Tiến hóa"',
        'check_q': lambda q: "khoa học tự nhiên" in q.lower() or "phát minh" in q.lower() or "tiền đề KHTN" in q.lower(),
        'matched': []
    },
    {
        'rule': 'Dấu hiệu "Tiền đề lý luận trực tiếp" -> Chọn "Triết học cổ điển Đức"',
        'check_q': lambda q: "lý luận trực tiếp" in q.lower() or "tiền đề lý luận" in q.lower(),
        'matched': []
    },
    {
        'rule': 'Dấu hiệu "Quyết định" -> Quy tắc "Thực thể 1 (Vật chất / Kinh tế / Tồn tại XH) quyết định Thực thể 2 (Ý thức / Chính trị / Ý thức XH)"',
        'check_q': lambda q: "quyết định" in q.lower() or "vai trò của" in q.lower(),
        'matched': []
    },
    {
        'rule': 'Dấu hiệu "Phương thức sản xuất" -> Chọn "Quyết định sự phát triển của xã hội"',
        'check_q': lambda q: "phương thức sản xuất" in q.lower(),
        'matched': []
    },
    {
        'rule': 'Dấu hiệu "Lực lượng sản xuất" -> Chọn "Yếu tố động nhất, cách mạng nhất"',
        'check_q': lambda q: "lực lượng sản xuất" in q.lower(),
        'matched': []
    },
    {
        'rule': 'Dấu hiệu "Quần chúng nhân dân" -> Chọn "Người sáng tạo ra lịch sử"',
        'check_q': lambda q: "quần chúng" in q.lower() or "nhân dân" in q.lower() or "vai trò cá nhân" in q.lower(),
        'matched': []
    }
]

for item in all_q:
    q_txt = item['q']
    for lh in loopholes:
        if lh['check_q'](q_txt):
            lh['matched'].append(item)

print("\n--- LOOPHOLE MATCH RESULTS ---")
for lh in loopholes:
    print(f"[{len(lh['matched'])} câu] {lh['rule']}")

