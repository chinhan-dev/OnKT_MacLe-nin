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

loopholes_refined = [
    {
        'id': 1,
        'q_label': '1. Đề hỏi về "Hêghen" (Hegel)',
        'a_label': 'Khoanh ngay <span class="kw-green">"Chủ nghĩa duy tâm khách quan"</span> hoặc <span class="kw-green">"Phép biện chứng"</span>',
        'check': lambda q: "hêghen" in q['q'].lower() or "hêghen" in " ".join([o['text'].lower() for o in q['options']])
    },
    {
        'id': 2,
        'q_label': '2. Đề hỏi về "Phoi-ơ-bắc" (L.Feuerbach)',
        'a_label': 'Khoanh ngay <span class="kw-green">"Chủ nghĩa duy vật siêu hình"</span> (hoặc nhân bản)',
        'check': lambda q: "phoi" in q['q'].lower() or "feuerbach" in q['q'].lower()
    },
    {
        'id': 3,
        'q_label': '3. Đề hỏi "Định nghĩa Vật chất của Lênin" / "Phạm trù vật chất"',
        'a_label': 'Khoanh ngay <span class="kw-green">"Thực tại khách quan"</span> hoặc <span class="kw-green">"Tồn tại độc lập với ý thức"</span>',
        'check': lambda q: ("thực tại khách quan" in q['correct_txt'].lower() or "độc lập với ý thức" in q['correct_txt'].lower() or "tồn tại khách quan" in q['correct_txt'].lower()) and "bổ sung" not in q['q'].lower()
    },
    {
        'id': 4,
        'q_label': '4. Đề hỏi "V.I. Lênin bổ sung và phát triển Triết học Mác"',
        'a_label': 'Khoanh ngay <span class="kw-green">"Chủ nghĩa tư bản độc quyền ra đời"</span>',
        'check': lambda q: "lênin bổ sung" in q['q'].lower() or "lênin phát triển" in q['q'].lower() or "độc quyền" in q['correct_txt'].lower()
    },
    {
        'id': 5,
        'q_label': '5. Đề hỏi về "Chủ nghĩa duy vật chất phác"',
        'a_label': 'Khoanh ngay <span class="kw-green">"Thời kỳ Cổ đại"</span> (Trực quan, cảm tính)',
        'check': lambda q: "chất phác" in q['q'].lower() or "chất phác" in q['correct_txt'].lower()
    },
    {
        'id': 6,
        'q_label': '6. Đề hỏi về "Vận động của vật chất"',
        'a_label': 'Khoanh ngay <span class="kw-green">"Phương thức tồn tại của vật chất"</span> (tuyệt đối, vĩnh viễn)',
        'check': lambda q: "vận động" in q['q'].lower()
    },
    {
        'id': 7,
        'q_label': '7. Đề hỏi về "Không gian và Thời gian"',
        'a_label': 'Khoanh ngay <span class="kw-green">"Hình thức tồn tại của vật chất"</span>',
        'check': lambda q: "không gian" in q['q'].lower() or "thời gian" in q['q'].lower()
    },
    {
        'id': 8,
        'q_label': '8. Đề hỏi "Bản chất & Nguồn gốc của Ý thức"',
        'a_label': 'Khoanh ngay <span class="kw-green">"Hình ảnh phản ánh tích cực, sáng tạo"</span> (mang tính chủ quan)',
        'check': lambda q: "ý thức" in q['q'].lower() and "ý thức xã hội" not in q['q'].lower() and "tồn tại xã hội" not in q['q'].lower()
    },
    {
        'id': 9,
        'q_label': '9. Đề hỏi vai trò của "Thực tiễn"',
        'a_label': 'Khoanh ngay <span class="kw-green">"Cơ sở, động lực, mục đích của nhận thức"</span>',
        'check': lambda q: "thực tiễn" in q['q'].lower()
    },
    {
        'id': 10,
        'q_label': '10. Đề hỏi "3 Phát minh Khoa học Tự nhiên" tiền đề Mác',
        'a_label': 'Khoanh ngay bộ 3: <span class="kw-green">Thuyết tế bào</span>, <span class="kw-green">Bảo toàn năng lượng</span>, <span class="kw-green">Tiến hóa Đácuyn</span>',
        'check': lambda q: "tiền đề" in q['q'].lower() or "khoa học tự nhiên" in q['q'].lower() or "phát minh" in q['q'].lower()
    },
    {
        'id': 11,
        'q_label': '11. Đề hỏi quan hệ "Quyết định" (Vật chất / Hạ tầng / Kinh tế)',
        'a_label': 'Áp dụng quy tắc: Thực thể Vật chất/Kinh tế/Hạ tầng luôn <span class="kw-green">QUYẾT ĐỊNH</span> Ý thức/Chính trị/Thượng tầng',
        'check': lambda q: "quyết định" in q['q'].lower()
    },
    {
        'id': 12,
        'q_label': '12. Đề hỏi "Phương thức sản xuất"',
        'a_label': 'Khoanh ngay <span class="kw-green">"Quyết định sự phát triển và biến đổi của xã hội"</span>',
        'check': lambda q: "phương thức sản xuất" in q['q'].lower()
    },
    {
        'id': 13,
        'q_label': '13. Đề hỏi "Lực lượng sản xuất"',
        'a_label': 'Khoanh ngay <span class="kw-green">"Yếu tố động nhất, cách mạng nhất"</span>',
        'check': lambda q: "lực lượng sản xuất" in q['q'].lower()
    },
    {
        'id': 14,
        'q_label': '14. Đề hỏi "Quần chúng nhân dân"',
        'a_label': 'Khoanh ngay <span class="kw-green">"Lực lượng sáng tạo ra lịch sử"</span>',
        'check': lambda q: "quần chúng" in q['q'].lower() or "nhân dân" in q['q'].lower()
    }
]

for lh in loopholes_refined:
    lh['matched'] = [item for item in all_q if lh['check'](item)]
    print(f"Rule {lh['id']}: [{len(lh['matched'])} câu] {lh['q_label']}")

