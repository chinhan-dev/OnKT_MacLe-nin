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
            'id': q['question_id'],
            'q': q['question'],
            'opts': {o['label']: o['text'] for o in q['options']},
            'correct': q['correct_option']
        })

print("=== 1. TẤT CẢ ĐỀU ĐÚNG / CẢ A, B, C ===")
for item in all_questions:
    opts = item['opts']
    correct = item['correct']
    for l, t in opts.items():
        if any(w in t.lower() for w in ["tất cả", "cả a, b, c", "cả 3"]):
            is_right = (l == correct)
            status = "✅ KHOANH TẤT CẢ" if is_right else f"⚠️ BẪY! Khoanh {correct} ('{opts[correct]}')"
            print(f"[{item['tab']} - Câu {item['id']}] {item['q'][:60]}... -> {l}: '{t}' => {status}")

