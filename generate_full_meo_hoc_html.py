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

def clean_q_text(txt):
    # Remove leading question numbers like "9. ", "10. ", "1. "
    return re.sub(r'^\d+[\.\s]+', '', txt).strip()

all_q = []
for tab_key, tab_data in data.items():
    tname = tab_names.get(tab_key, tab_key)
    for q in tab_data['questions']:
        all_q.append({
            'tab': tname,
            'tab_key': tab_key,
            'id': q['question_id'],
            'q': clean_q_text(q['question']),
            'options': q['options'],
            'opts': {o['label']: o['text'] for o in q['options']},
            'correct': q['correct_option'],
            'selected': q.get('selected_option')
        })

# Keywords to highlight in GREEN in correct answers
keywords = [
    "thực tại khách quan", "giải thích và cải tạo thế giới", "triết học cổ điển đức",
    "hạt nhân lý luận", "bất khả tri", "phép biện chứng", "duy tâm khách quan",
    "duy vật biện chứng", "duy vật lịch sử", "lực lượng sản xuất", "quan hệ sản xuất",
    "kiến trúc thượng tầng", "cơ sở hạ tầng", "quần chúng nhân dân", "tồn tại xã hội",
    "ý thức xã hội", "thực tiễn", "bảo toàn và chuyển hóa năng lượng", "thuyết tế bào",
    "học thuyết tiến hóa", "duy vật chất phác", "phương thức sản xuất", "độc lập với ý thức",
    "tồn tại khách quan", "nhận thức thế giới", "quyết định ý thức", "cải tạo thế giới",
    "kinh viện", "kinh tế chính trị", "chủ nghĩa xã hội không tưởng", "phân chia trình độ"
]

def highlight_keywords(text):
    pattern = re.compile("|".join(re.escape(k) for k in keywords), re.IGNORECASE)
    def repl(m):
        return f'<span class="kw-green">{m.group(0)}</span>'
    return pattern.sub(repl, text)

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
    
    if len(longest_txt) - len(second_txt) >= 20 and len(longest_txt) > 55:
        if correct == longest_lbl:
            longest_rights.append((item, longest_lbl, longest_txt))
        else:
            longest_tricks.append((item, longest_lbl, longest_txt, correct, opts[correct]))

# 3. Negative questions ("SAI", "KHÔNG ĐÚNG")
negative_questions = []
for item in all_q:
    ql = item['q'].lower()
    if "sai" in ql or "không đúng" in ql or "không thuộc" in ql or "khẳng định sai" in ql or "quan điểm sai" in ql:
        negative_questions.append(item)

# Helper to render all 4 options for a question card with Green Keyword Highlight
def render_all_options(item, trick_lbl=None):
    correct_lbl = item['correct']
    html_out = '<div class="options-container">'
    
    for opt in item['options']:
        lbl = opt['label']
        txt = opt['text']
        
        is_correct = (lbl == correct_lbl)
        is_trick = (lbl == trick_lbl)
        
        opt_class = "opt-item"
        badge_html = ""
        
        display_txt = txt
        if is_correct:
            opt_class += " is-correct"
            display_txt = highlight_keywords(txt)
            badge_html = '<span class="badge badge-correct"><i class="fa-solid fa-check"></i> ĐÁP ÁN ĐÚNG CHUẨN</span>'
        elif is_trick:
            opt_class += " is-trick"
            badge_html = '<span class="badge badge-trick"><i class="fa-solid fa-xmark"></i> BẪY LỪA (SAI)</span>'
          
        html_out += f'''
          <div class="{opt_class}">
            <span class="opt-label">{lbl}</span>
            <span class="opt-text">{display_txt}</span>
            {badge_html}
          </div>
        '''
        
    html_out += '</div>'
    return html_out

# Build complete HTML
html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mẹo Học & Quy Tắc Khoanh Trắc Nghiệm Triết Học Mác - Lênin (Đầy Đủ All Câu)</title>

  <!-- Clean typography -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: #f8fafc;
      color: #0f172a;
      line-height: 1.6;
      padding: 24px 40px;
      max-width: 1440px;
      margin: 0 auto;
    }}

    .top-nav {{
      margin-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .btn-back {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: #2563eb;
      text-decoration: none;
      font-weight: 700;
      font-size: 0.9rem;
      padding: 10px 20px;
      border: 1px solid #bfdbfe;
      border-radius: 9999px;
      background-color: #eff6ff;
      transition: all 0.2s;
    }}

    .btn-back:hover {{
      background-color: #2563eb;
      color: #ffffff;
      border-color: #2563eb;
    }}

    .section {{
      margin-bottom: 40px;
    }}

    .section-title {{
      font-size: 1.3rem;
      font-weight: 800;
      color: #1e3a8a;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 10px;
      padding-bottom: 10px;
      border-bottom: 2px solid #e2e8f0;
    }}

    .alert-box {{
      background-color: #fffbeb;
      border-left: 4px solid #f59e0b;
      padding: 16px 20px;
      border-radius: 8px;
      margin-bottom: 20px;
      font-size: 0.95rem;
      color: #92400e;
      border: 1px solid #fef3c7;
    }}

    .alert-box.success {{
      background-color: #ecfdf5;
      border-left-color: #10b981;
      color: #065f46;
      border-color: #a7f3d0;
    }}

    .sub-heading {{
      font-size: 1.05rem;
      font-weight: 700;
      margin-top: 24px;
      margin-bottom: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .sub-heading.danger {{ color: #dc2626; }}
    .sub-heading.success {{ color: #059669; }}

    /* 2-Column Grid for Cards */
    .q-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(620px, 1fr));
      gap: 16px;
    }}

    .q-card {{
      border: 1px solid #cbd5e1;
      border-radius: 12px;
      padding: 20px;
      background-color: #ffffff;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 14px;
    }}

    /* Fixed Clean Question Header Row */
    .q-header {{
      display: flex;
      flex-direction: row;
      align-items: flex-start;
      gap: 10px;
    }}

    .q-tag {{
      font-size: 0.75rem;
      font-weight: 800;
      padding: 4px 12px;
      border-radius: 9999px;
      background-color: #eff6ff;
      color: #1d4ed8;
      border: 1px solid #bfdbfe;
      white-space: nowrap; /* Prevent tag from dropping or wrapping */
      flex-shrink: 0;      /* Prevent tag from shrinking */
    }}

    /* Distinct Blue Question Text for perfect readability */
    .q-text {{
      font-size: 1.02rem;
      font-weight: 700;
      color: #1d4ed8; /* Blue Question Text */
      line-height: 1.4;
      flex: 1;
    }}

    /* Options Container - Full 4 Options */
    .options-container {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .opt-item {{
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 14px;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
      background-color: #f8fafc;
      font-size: 0.9rem;
      position: relative;
    }}

    .opt-label {{
      width: 26px;
      height: 26px;
      border-radius: 50%;
      background-color: #ffffff;
      border: 1px solid #cbd5e1;
      font-weight: 700;
      font-size: 0.82rem;
      color: #334155;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}

    .opt-text {{
      flex: 1;
      color: #334155;
    }}

    /* GREEN KEYWORD HIGHLIGHT STYLE */
    .kw-green {{
      background-color: #d1fae5;
      color: #047857;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid #a7f3d0;
      box-shadow: 0 1px 2px rgba(16, 185, 129, 0.1);
    }}

    /* Highlight Correct Option */
    .opt-item.is-correct {{
      background-color: #ecfdf5;
      border-color: #10b981;
    }}

    .opt-item.is-correct .opt-label {{
      background-color: #10b981;
      color: #ffffff;
      border-color: #10b981;
    }}

    .opt-item.is-correct .opt-text {{
      color: #065f46;
      font-weight: 700;
    }}

    /* Highlight Trick Option */
    .opt-item.is-trick {{
      background-color: #fef2f2;
      border-color: #ef4444;
    }}

    .opt-item.is-trick .opt-label {{
      background-color: #ef4444;
      color: #ffffff;
      border-color: #ef4444;
    }}

    .opt-item.is-trick .opt-text {{
      color: #b91c1c;
      font-weight: 600;
      text-decoration: line-through;
    }}

    .badge {{
      font-size: 0.72rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 9999px;
      margin-left: auto;
      white-space: nowrap;
    }}

    .badge-correct {{
      background-color: #10b981;
      color: #ffffff;
    }}

    .badge-trick {{
      background-color: #ef4444;
      color: #ffffff;
    }}

    .keyword-table {{
      width: 100%;
      border-collapse: collapse;
      background-color: #ffffff;
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid #e2e8f0;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .keyword-table th, .keyword-table td {{
      border: 1px solid #e2e8f0;
      padding: 14px 18px;
      text-align: left;
      font-size: 0.92rem;
    }}

    .keyword-table th {{
      background-color: #eff6ff;
      color: #1e40af;
      font-weight: 800;
    }}

    .keyword-table td.q-col {{
      color: #1d4ed8;
      font-weight: 700;
      width: 45%;
    }}

    .keyword-table td.a-col {{
      color: #047857;
      font-weight: 700;
      width: 55%;
    }}

    .keyword-table tr:nth-child(even) {{
      background-color: #f8fafc;
    }}
  </style>
</head>
<body>

  <!-- Top Navigation -->
  <div class="top-nav">
    <a href="index.html" class="btn-back">
      <i class="fa-solid fa-arrow-left"></i> Quay lại LMS Ôn Luyện
    </a>
  </div>

  <!-- SECTION 1 -->
  <div class="section">
    <div class="section-title">
      <i class="fa-solid fa-triangle-exclamation" style="color: #ef4444;"></i>
      PHẦN 1: DẠNG CÂU HỎI "TẤT CẢ ĐỀU ĐÚNG / TẤT CẢ..." (Toàn bộ {len(tat_ca_tricks) + len(tat_ca_rights)} câu)
    </div>
    
    <div class="alert-box">
      ⚠️ <strong>CẢNH BÁO QUAN TRỌNG:</strong> Trong ngân hàng 331 câu hỏi Triết học Mác - Lênin, có 6 câu chứa lựa chọn "Tất cả...". Tuy nhiên:
      <br>• Chỉ có <strong>1 CÂU DUY NHẤT</strong> khoanh đáp án "Tất cả...".
      <br>• Có <strong>5 CÂU LÀ BẪY LỪA</strong> (Khoanh "Tất cả" là SAI, phải khoanh đáp án khác)!
    </div>

    <div class="sub-heading danger">
      <i class="fa-solid fa-xmark-circle"></i>
      1.1. Danh sách ĐẦY ĐỦ 5 CÂU BẪY "Tất cả..." (KHÔNG ĐƯỢC khoanh Tất cả!):
    </div>
    <div class="q-grid">
"""

for item, tat_ca_lbl, tat_ca_txt, correct, correct_txt in tat_ca_tricks:
    opts_html = render_all_options(item, trick_lbl=tat_ca_lbl)
    html += f"""
      <div class="q-card">
        <div class="q-header">
          <span class="q-tag">{item['tab']} - Câu {item['id']}</span>
          <div class="q-text">{item['q']}</div>
        </div>
        {opts_html}
      </div>
    """

html += """
    </div>

    <div class="sub-heading success">
      <i class="fa-solid fa-check-circle"></i>
      1.2. Câu DUY NHẤT được khoanh "Tất cả...":
    </div>
    <div class="q-grid">
"""

for item, l, t in tat_ca_rights:
    opts_html = render_all_options(item)
    html += f"""
      <div class="q-card">
        <div class="q-header">
          <span class="q-tag">{item['tab']} - Câu {item['id']}</span>
          <div class="q-text">{item['q']}</div>
        </div>
        {opts_html}
      </div>
    """

html += f"""
    </div>
  </div>

  <!-- SECTION 2 -->
  <div class="section">
    <div class="section-title">
      <i class="fa-solid fa-ruler" style="color: #2563eb;"></i>
      PHẦN 2: CÁC CÂU QUY TẮC "ĐÁP ÁN DÀI NHẤT" (Toàn bộ {len(longest_rights) + len(longest_tricks)} câu)
    </div>

    <div class="alert-box success">
      💡 <strong>QUY TẮC VÀNG:</strong> Các đáp án dài vượt trội có tỷ lệ đúng rất cao ({len(longest_rights)} câu). Tuy nhiên có {len(longest_tricks)} câu là bẫy dài nhất!
    </div>

    <div class="sub-heading success">
      <i class="fa-solid fa-check-double"></i>
      2.1. ĐẦY ĐỦ TOÀN BỘ {len(longest_rights)} CÂU có Đáp án dài vượt trội là ĐÚNG CHUẨN:
    </div>
    <div class="q-grid">
"""

for item, l, t in longest_rights:
    opts_html = render_all_options(item)
    html += f"""
      <div class="q-card">
        <div class="q-header">
          <span class="q-tag">{item['tab']} - Câu {item['id']}</span>
          <div class="q-text">{item['q']}</div>
        </div>
        {opts_html}
      </div>
    """

html += f"""
    </div>

    <div class="sub-heading danger">
      <i class="fa-solid fa-triangle-exclamation"></i>
      2.2. ĐẦY ĐỦ TOÀN BỘ {len(longest_tricks)} CÂU BẪY DÀI NHẤT! (Dài nhất nhưng SAI - Khoanh câu khác):
    </div>
    <div class="q-grid">
"""

for item, longest_lbl, longest_txt, correct, correct_txt in longest_tricks:
    opts_html = render_all_options(item, trick_lbl=longest_lbl)
    html += f"""
      <div class="q-card">
        <div class="q-header">
          <span class="q-tag">{item['tab']} - Câu {item['id']}</span>
          <div class="q-text">{item['q']}</div>
        </div>
        {opts_html}
      </div>
    """

html += f"""
    </div>
  </div>

  <!-- SECTION 3 -->
  <div class="section">
    <div class="section-title">
      <i class="fa-solid fa-key" style="color: #d97706;"></i>
      PHẦN 3: BẢNG TỪ KHÓA VÀNG (NHÌN THẤY LÀ KHOANH NGAY - 100% CHÍNH XÁC)
    </div>

    <table class="keyword-table">
      <thead>
        <tr>
          <th>Từ khóa trong Câu hỏi (Màu Xanh Dương)</th>
          <th>Từ khóa / Đáp án ĐÚNG CHUẨN Cần Khoanh (Highlight Xanh Lá)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="q-col">Nhiệm vụ của triết học</td>
          <td class="a-col"><span class="kw-green">"Giải thích và cải tạo thế giới"</span></td>
        </tr>
        <tr>
          <td class="q-col">Tiền đề lý luận trực tiếp ra đời Triết học Mác</td>
          <td class="a-col"><span class="kw-green">"Triết học cổ điển Đức"</span> (Hêghen & Phoi-ơ-bắc)</td>
        </tr>
        <tr>
          <td class="q-col">Thế giới quan của Hêghen</td>
          <td class="a-col"><span class="kw-green">"Chủ nghĩa duy tâm khách quan"</span></td>
        </tr>
        <tr>
          <td class="q-col">Hạt nhân hợp lý Hêghen Mác kế thừa</td>
          <td class="a-col"><span class="kw-green">"Phép biện chứng"</span></td>
        </tr>
        <tr>
          <td class="q-col">Thế giới quan của Phoi-ơ-bắc (L.Feuerbach)</td>
          <td class="a-col"><span class="kw-green">"Chủ nghĩa duy vật"</span> (duy vật siêu hình)</td>
        </tr>
        <tr>
          <td class="q-col">Triết học đóng vai trò gì trong thế giới quan</td>
          <td class="a-col"><span class="kw-green">"Hạt nhân lý luận"</span></td>
        </tr>
        <tr>
          <td class="q-col">Phủ nhận khả năng nhận thức thế giới</td>
          <td class="a-col"><span class="kw-green">"Trường phái bất khả tri"</span> (Agnosticism)</td>
        </tr>
        <tr>
          <td class="q-col">3 phát minh KHTN tiền đề</td>
          <td class="a-col"><span class="kw-green">Thuyết tế bào</span>, <span class="kw-green">Định luật bảo toàn năng lượng</span>, <span class="kw-green">Học thuyết tiến hóa</span> Đácuyn</td>
        </tr>
        <tr>
          <td class="q-col">Định nghĩa vật chất của Lênin</td>
          <td class="a-col">"Là một phạm trù triết học dùng để chỉ <span class="kw-green">thực tại khách quan</span>..."</td>
        </tr>
        <tr>
          <td class="q-col">Phân chia trình độ tiến bộ xã hội căn cứ vào</td>
          <td class="a-col">"<span class="kw-green">Trình độ phát triển của lực lượng sản xuất</span>"</td>
        </tr>
        <tr>
          <td class="q-col">Hình thức triết học Châu Âu Trung cổ</td>
          <td class="a-col">"<span class="kw-green">Triết học kinh viện</span>" (Scholasticism)</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- SECTION 4 -->
  <div class="section">
    <div class="section-title">
      <i class="fa-solid fa-circle-exclamation" style="color: #6b7280;"></i>
      PHẦN 4: ĐẦY ĐỦ CÁC CÂU HỎI BẪY PHỦ ĐỊNH ("SAI", "KHÔNG ĐÚNG") - (Toàn bộ {len(negative_questions)} câu)
    </div>

    <div class="alert-box">
      ⚠️ Khi đề bài hỏi <strong>"Nhận xét/Khẳng định nào SAI"</strong>, tuyệt đối không khoanh đáp án đúng! Hãy tìm câu phát biểu có từ <em>"tách rời"</em>, <em>"thống nhất ở ý thức"</em>, <em>"không có vai trò"</em> hoặc <em>"lắp ghép kết hợp"</em> để khoanh.
    </div>

    <div class="q-grid">
"""

for item in negative_questions:
    opts_html = render_all_options(item)
    html += f"""
      <div class="q-card">
        <div class="q-header">
          <span class="q-tag">{item['tab']} - Câu {item['id']}</span>
          <div class="q-text">{item['q']}</div>
        </div>
        {opts_html}
      </div>
    """

html += """
    </div>
  </div>

</body>
</html>
"""

with open('meo_hoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Generated full meo_hoc.html with clean question title row (no text drop or duplicate numbers).")
