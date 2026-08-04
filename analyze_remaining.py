import json, re

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
            'uid': f"{tab_key}_{q['question_id']}",
            'tab': tname,
            'tab_key': tab_key,
            'id': q['question_id'],
            'q': q['question'],
            'options': q['options'],
            'opts': {o['label']: o['text'] for o in q['options']},
            'correct': q['correct_option'],
            'selected': q.get('selected_option')
        })

# Track covered UIDs
covered_uids = set()

# Section 1
for item in all_q:
    for l, t in item['opts'].items():
        tl = t.lower()
        if "tất cả" in tl or "cả a, b, c" in tl or "cả 3" in tl or "cả a và b" in tl:
            covered_uids.add(item['uid'])

# Section 2
for item in all_q:
    sorted_opts = sorted(item['opts'].items(), key=lambda x: len(x[1]), reverse=True)
    longest_lbl, longest_txt = sorted_opts[0]
    second_lbl, second_txt = sorted_opts[1]
    if len(longest_txt) - len(second_txt) >= 20 and len(longest_txt) > 55:
        covered_uids.add(item['uid'])

# Section 4
for item in all_q:
    ql = item['q'].lower()
    if "sai" in ql or "không đúng" in ql or "không thuộc" in ql or "khẳng định sai" in ql or "quan điểm sai" in ql:
        covered_uids.add(item['uid'])

remaining_q = [item for item in all_q if item['uid'] not in covered_uids]

print(f"Total: {len(all_q)}")
print(f"Covered in Sec 1,2,4: {len(covered_uids)}")
print(f"Remaining for Sec 5: {len(remaining_q)}")

# Sub-categorize Section 5 questions
cat_vatchat = []
cat_biencheng = []
cat_duyvatlichsu = []
cat_trietgia = []
cat_khac = []

for item in remaining_q:
    ql = item['q'].lower()
    opts_l = " ".join([t.lower() for t in item['opts'].values()])
    
    if any(w in ql or w in opts_l for w in ["vật chất", "ý thức", "phản ánh", "thực tại khách quan", "vận động", "không gian", "thời gian", "thực tiễn"]):
        cat_vatchat.append(item)
    elif any(w in ql or w in opts_l for w in ["mâu thuẫn", "lượng", "chất", "phủ định", "cái chung", "bản chất", "nguyên nhân", "nội dung", "khả năng"]):
        cat_biencheng.append(item)
    elif any(w in ql or w in opts_l for w in ["phương thức sản xuất", "lực lượng sản xuất", "quan hệ sản xuất", "cơ sở hạ tầng", "kiến trúc thượng tầng", "tồn tại xã hội", "ý thức xã hội", "quần chúng", "giai cấp"]):
        cat_duyvatlichsu.append(item)
    elif any(w in ql or w in opts_l for w in ["hêghen", "phoi", "mác", "ăngghen", "lênin", "cổ đại", "trung cổ", "khai sáng"]):
        cat_trietgia.append(item)
    else:
        cat_khac.append(item)

print(f"\n--- Section 5 Breakdown ---")
print(f"5.1 Vật chất - Ý thức - Thực tiễn: {len(cat_vatchat)} câu")
print(f"5.2 Phép biện chứng duy vật (Quy luật & Cặp phạm trù): {len(cat_biencheng)} câu")
print(f"5.3 Chủ nghĩa duy vật lịch sử (Kinh tế, Xã hội, Giai cấp): {len(cat_duyvatlichsu)} câu")
print(f"5.4 Triết gia & Lịch sử triết học: {len(cat_trietgia)} câu")
print(f"5.5 Các câu ôn tập tổng hợp còn lại: {len(cat_khac)} câu")

