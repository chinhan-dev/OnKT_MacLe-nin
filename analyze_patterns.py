import json

with open('quiz_data.js', 'r', encoding='utf-8') as f:
    content = f.read()
json_str = content.replace("window.QUIZ_DATA = ", "").rstrip(";")
data = json.loads(json_str)

all_questions = []
tab_names = {
    'bai1': 'Bài 1',
    'bai2': 'Bài 2',
    'bai3': 'Bài 3',
    'kt1': 'Đề KT 1',
    'kt2': 'Đề KT 2',
    'kt3': 'Đề KT 3'
}

for tab_key, tab_data in data.items():
    tname = tab_names.get(tab_key, tab_key)
    for q in tab_data['questions']:
        all_questions.append({
            'tab': tname,
            'tab_key': tab_key,
            'id': q['question_id'],
            'q': q['question'],
            'opts': {o['label']: o['text'] for o in q['options']},
            'correct': q['correct_option'],
            'selected': q.get('selected_option')
        })

print(f"Total questions loaded: {len(all_questions)}")

# 1. Analyze "Tất cả" / "Cả A, B, C"
tat_ca_correct = []
tat_ca_trick = []

for item in all_questions:
    opts = item['opts']
    correct = item['correct']
    
    tat_ca_lbl = None
    for l, t in opts.items():
        tl = t.lower()
        if "tất cả" in tl or "cả a, b, c" in tl or "cả 3" in tl or "cả a và b" in tl:
            tat_ca_lbl = l
            break
            
    if tat_ca_lbl:
        if correct == tat_ca_lbl:
            tat_ca_correct.append((item, tat_ca_lbl))
        else:
            tat_ca_trick.append((item, tat_ca_lbl, correct))

print(f"\n--- 'Tất cả đều đúng' Analysis ---")
print(f"Khoanh 'Tất cả': {len(tat_ca_correct)} câu")
print(f"BẪY! Không được khoanh 'Tất cả': {len(tat_ca_trick)} câu")

# 2. Analyze "Đáp án dài nhất"
longest_is_correct = []
longest_is_trick = []

for item in all_questions:
    opts = item['opts']
    correct = item['correct']
    
    # Sort options by length
    sorted_opts = sorted(opts.items(), key=lambda x: len(x[1]), reverse=True)
    longest_lbl, longest_txt = sorted_opts[0]
    second_longest_lbl, second_longest_txt = sorted_opts[1]
    
    # Check if longest is significantly longer (at least 15 chars longer)
    if len(longest_txt) - len(second_longest_txt) >= 15:
        if correct == longest_lbl:
            longest_is_correct.append((item, longest_lbl, longest_txt, len(longest_txt)))
        else:
            longest_is_trick.append((item, longest_lbl, correct, longest_txt, opts[correct]))

print(f"\n--- 'Đáp án dài nhất' Analysis ---")
print(f"Đáp án vượt trội dài nhất ĐÚNG: {len(longest_is_correct)} câu")
print(f"BẪY! Dài nhất nhưng SAI (khoanh câu khác): {len(longest_is_trick)} câu")

# 3. Analyze Negative questions ("sai", "không đúng")
negative_qs = []
for item in all_questions:
    ql = item['q'].lower()
    if "sai" in ql or "không đúng" in ql or "không thuộc" in ql or "khẳng định sai" in ql:
        negative_qs.append(item)

print(f"\n--- Câu hỏi bẫy Phủ định ('SAI', 'KHÔNG ĐÚNG') ---")
print(f"Tổng số câu phủ định: {len(negative_qs)} câu")

