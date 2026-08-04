import json

with open('quiz_data.js', 'r', encoding='utf-8') as f:
    content = f.read()
json_str = content.replace("window.QUIZ_DATA = ", "").rstrip(";")
data = json.loads(json_str)

tab_names = {
    'bai1': 'Bài 1',
    'bai2': 'Bài 2',
    'bai3': 'Bài 3',
    'kt1': 'Đề KT 1',
    'kt2': 'Đề KT 2',
    'kt3': 'Đề KT 3'
}

all_q = []
for tab_key, tab_data in data.items():
    tname = tab_names.get(tab_key, tab_key)
    for q in tab_data['questions']:
        all_q.append({
            'tab': tname,
            'tab_key': tab_key,
            'id': q['question_id'],
            'q': q['question'],
            'opts': {o['label']: o['text'] for o in q['options']},
            'correct': q['correct_option'],
            'exp': q.get('explanation', '')
        })

# 1. "Tất cả" analysis
tat_ca_tricks = []
tat_ca_rights = []

for item in all_q:
    opts = item['opts']
    correct = item['correct']
    for l, t in opts.items():
        tl = t.lower()
        if "tất cả" in tl or "cả a, b, c" in tl or "cả 3" in tl or "cả a và b" in tl:
            if l == correct:
                tat_ca_rights.append((item, l, t))
            else:
                tat_ca_tricks.append((item, l, t, correct, opts[correct]))

# 2. Longest option analysis
longest_rights = []
longest_tricks = []

for item in all_q:
    opts = item['opts']
    correct = item['correct']
    sorted_opts = sorted(opts.items(), key=lambda x: len(x[1]), reverse=True)
    longest_lbl, longest_txt = sorted_opts[0]
    second_lbl, second_txt = sorted_opts[1]
    
    # Significant difference in length (at least 25 characters longer than 2nd longest)
    if len(longest_txt) - len(second_txt) >= 25 and len(longest_txt) > 60:
        if correct == longest_lbl:
            longest_rights.append((item, longest_lbl, longest_txt))
        else:
            longest_tricks.append((item, longest_lbl, longest_txt, correct, opts[correct]))

# 3. Negative questions ("SAI", "KHÔNG ĐÚNG")
negative_questions = []
for item in all_q:
    ql = item['q'].lower()
    if "sai" in ql or "không đúng" in ql or "không thuộc" in ql or "khẳng định sai" in ql:
        negative_questions.append(item)

# 4. Golden Keywords
keywords = [
    ("Giải thích và cải tạo thế giới", "Nhiệm vụ của triết học"),
    ("Triết học cổ điển Đức", "Tiền đề lý luận trực tiếp ra đời Triết học Mác"),
    ("Duy tâm khách quan", "Thế giới quan triết học của Hêghen"),
    ("Duy vật", "Thế giới quan của Phoi-ơ-bắc (L.Feuerbach)"),
    ("Hạt nhân lý luận", "Triết học giữ vai trò hạt nhân lý luận trong thế giới quan"),
    ("Trường phái bất khả tri", "Học thuyết phủ nhận khả năng nhận thức thế giới"),
    ("Học thuyết tiến hóa, thuyết tế bào, định luật bảo toàn", "3 phát minh KHTN tiền đề"),
    ("Vật chất là phạm trù triết học dùng để chỉ thực tại khách quan", "Định nghĩa vật chất của Lênin"),
    ("Trình độ phát triển của lực lượng sản xuất", "Căn cứ phân chia trình độ tiến bộ xã hội"),
    ("Thực tiễn", "Cơ sở, động lực, mục đích của nhận thức và tiêu chuẩn kiểm tra định chân lý")
]

print(f"Tat ca: {len(tat_ca_rights)} right, {len(tat_ca_tricks)} tricks")
print(f"Longest: {len(longest_rights)} right, {len(longest_tricks)} tricks")
print(f"Negative Qs: {len(negative_questions)}")
