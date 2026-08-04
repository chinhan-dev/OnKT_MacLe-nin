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
    return re.sub(r'^\d+[\.\s]+', '', txt).strip()

all_q = []
for tab_key, tab_data in data.items():
    tname = tab_names.get(tab_key, tab_key)
    for q in tab_data['questions']:
        all_q.append({
            'uid': f"{tab_key}_{q['question_id']}",
            'tab': tname,
            'tab_key': tab_key,
            'id': q['question_id'],
            'q': clean_q_text(q['question']),
            'options': q['options'],
            'opts': {o['label']: o['text'] for o in q['options']},
            'correct': q['correct_option'],
            'selected': q.get('selected_option')
        })

keywords = [
    "thực tại khách quan", "giải thích và cải tạo thế giới", "triết học cổ điển đức",
    "hạt nhân lý luận", "bất khả tri", "phép biện chứng", "duy tâm khách quan",
    "duy vật biện chứng", "duy vật lịch sử", "lực lượng sản xuất", "quan hệ sản xuất",
    "kiến trúc thượng tầng", "cơ sở hạ tầng", "quần chúng nhân dân", "tồn tại xã hội",
    "ý thức xã hội", "thực tiễn", "bảo toàn và chuyển hóa năng lượng", "thuyết tế bào",
    "học thuyết tiến hóa", "duy vật chất phác", "phương thức sản xuất", "độc lập với ý thức",
    "tồn tại khách quan", "nhận thức thế giới", "quyết định ý thức", "cải tạo thế giới",
    "kinh viện", "kinh tế chính trị", "chủ nghĩa xã hội không tưởng", "phân chia trình độ",
    "phản ánh", "vận động", "không gian", "thời gian", "mâu thuẫn", "lượng", "chất",
    "phủ định của phủ định", "cái chung", "cái riêng", "bản chất", "hiện tượng",
    "nguyên nhân", "kết quả", "nội dung", "hình thức", "tất nhiên", "ngẫu nhiên",
    "khả năng", "thực tế", "đấu tranh giai cấp", "hình thái kinh tế - xã hội", "triết học kinh viện"
]

def highlight_keywords(text):
    pattern = re.compile("|".join(re.escape(k) for k in keywords), re.IGNORECASE)
    def repl(m):
        return f'<span class="kw-green">{m.group(0)}</span>'
    return pattern.sub(repl, text)

# Tracking covered UIDs
sec1_tricks, sec1_rights = [], []
sec2_rights, sec2_tricks = [], []
sec4_qs = []
covered_uids = set()

# Section 1
for item in all_q:
    opts = item['opts']
    correct = item['correct']
    for l, t in opts.items():
        tl = t.lower()
        if "tất cả" in tl or "cả a, b, c" in tl or "cả 3" in tl or "cả a và b" in tl:
            covered_uids.add(item['uid'])
            if l == correct:
                sec1_rights.append((item, l, t))
            else:
                sec1_tricks.append((item, l, t, correct, opts[correct]))

# Section 2
for item in all_q:
    if item['uid'] in covered_uids: continue
    opts = item['opts']
    correct = item['correct']
    sorted_opts = sorted(opts.items(), key=lambda x: len(x[1]), reverse=True)
    longest_lbl, longest_txt = sorted_opts[0]
    second_lbl, second_txt = sorted_opts[1]
    if len(longest_txt) - len(second_txt) >= 20 and len(longest_txt) > 55:
        covered_uids.add(item['uid'])
        if correct == longest_lbl:
            sec2_rights.append((item, longest_lbl, longest_txt))
        else:
            sec2_tricks.append((item, longest_lbl, longest_txt, correct, opts[correct]))

# Section 4
for item in all_q:
    if item['uid'] in covered_uids: continue
    ql = item['q'].lower()
    if "sai" in ql or "không đúng" in ql or "không thuộc" in ql or "khẳng định sai" in ql or "quan điểm sai" in ql:
        covered_uids.add(item['uid'])
        sec4_qs.append(item)

# Section 5: ALL Remaining Questions
remaining_qs = [item for item in all_q if item['uid'] not in covered_uids]

# Sub-categorize Section 5
sec5_1 = [] # Vật chất - Ý thức - Thực tiễn
sec5_2 = [] # Phép biện chứng
sec5_3 = [] # Chủ nghĩa duy vật lịch sử
sec5_4 = [] # Triết gia & Lịch sử triết học
sec5_5 = [] # Các câu còn lại

for item in remaining_qs:
    ql = item['q'].lower()
    opts_l = " ".join([t.lower() for t in item['opts'].values()])
    
    if any(w in ql or w in opts_l for w in ["vật chất", "ý thức", "phản ánh", "thực tại khách quan", "vận động", "không gian", "thời gian", "thực tiễn", "cảm giác", "tư duy"]):
        sec5_1.append(item)
    elif any(w in ql or w in opts_l for w in ["mâu thuẫn", "lượng", "chất", "phủ định", "cái chung", "cái riêng", "bản chất", "hiện tượng", "nguyên nhân", "kết quả", "nội dung", "hình thức", "tất nhiên", "ngẫu nhiên", "khả năng", "thực tế"]):
        sec5_2.append(item)
    elif any(w in ql or w in opts_l for w in ["phương thức sản xuất", "lực lượng sản xuất", "quan hệ sản xuất", "cơ sở hạ tầng", "kiến trúc thượng tầng", "tồn tại xã hội", "ý thức xã hội", "quần chúng", "giai cấp", "hình thái kinh tế"]):
        sec5_3.append(item)
    elif any(w in ql or w in opts_l for w in ["hêghen", "phoi", "mác", "ăngghen", "lênin", "cổ đại", "trung cổ", "khai sáng", "phục hưng"]):
        sec5_4.append(item)
    else:
        sec5_5.append(item)

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

def render_grid_section(items):
    out = '<div class="q-grid">'
    for item in items:
        opts_html = render_all_options(item)
        out += f'''
          <div class="q-card">
            <div class="q-header">
              <span class="q-tag">{item['tab']} - Câu {item['id']}</span>
              <div class="q-text">{item['q']}</div>
            </div>
            {opts_html}
          </div>
        '''
    out += '</div>'
    return out

# Build HTML with 13 Golden Loopholes in Tab 3
html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mẹo Học & Quy Tắc Khoanh Trắc Nghiệm Triết Học Mác - Lênin (5 Tab Thon Gọn + Lỗ Hổng Câu Hỏi)</title>

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
      padding: 20px 40px;
      max-width: 1440px;
      margin: 0 auto;
    }}

    .top-nav {{
      margin-bottom: 16px;
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
      font-size: 0.85rem;
      padding: 6px 16px;
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

    /* ULTRA-THIN SLEEK 5 TABS NAVIGATION BAR */
    .tab-bar {{
      position: sticky;
      top: 10px;
      z-index: 100;
      background-color: #ffffff;
      padding: 4px;
      border-radius: 9999px;
      border: 1px solid #cbd5e1;
      display: flex;
      justify-content: space-between;
      gap: 6px;
      margin-bottom: 20px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }}

    .tab-item {{
      flex: 1;
      padding: 6px 12px;
      border-radius: 9999px;
      border: none;
      background-color: transparent;
      color: #475569;
      font-size: 0.8rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      gap: 6px;
      white-space: nowrap;
      transition: all 0.2s ease;
    }}

    .tab-item i {{
      font-size: 0.9rem;
    }}

    .tab-item small {{
      font-size: 0.7rem;
      font-weight: 600;
      opacity: 0.8;
      background-color: rgba(0,0,0,0.06);
      padding: 1px 6px;
      border-radius: 9999px;
    }}

    .tab-item:hover {{
      color: #2563eb;
      background-color: #eff6ff;
    }}

    .tab-item.active {{
      background: linear-gradient(135deg, #2563eb, #1d4ed8);
      color: #ffffff;
      box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
    }}

    .tab-item.active small {{
      background-color: rgba(255,255,255,0.25);
      color: #ffffff;
    }}

    .tab-content {{
      display: none;
    }}

    .tab-content.active {{
      display: block;
    }}

    .section {{
      margin-bottom: 40px;
    }}

    .section-title {{
      font-size: 1.25rem;
      font-weight: 800;
      color: #1e3a8a;
      margin-bottom: 14px;
      display: flex;
      align-items: center;
      gap: 10px;
      padding-bottom: 8px;
      border-bottom: 2px solid #e2e8f0;
    }}

    .alert-box {{
      background-color: #fffbeb;
      border-left: 4px solid #f59e0b;
      padding: 12px 16px;
      border-radius: 8px;
      margin-bottom: 16px;
      font-size: 0.9rem;
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
      font-size: 1.02rem;
      font-weight: 800;
      margin-top: 22px;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .sub-heading.danger {{ color: #dc2626; }}
    .sub-heading.success {{ color: #059669; }}
    .sub-heading.primary {{ color: #2563eb; }}

    /* 2-Column Grid for Cards */
    .q-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(620px, 1fr));
      gap: 14px;
    }}

    .q-card {{
      border: 1px solid #cbd5e1;
      border-radius: 12px;
      padding: 16px 18px;
      background-color: #ffffff;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 12px;
    }}

    .q-header {{
      display: flex;
      flex-direction: row;
      align-items: flex-start;
      gap: 10px;
    }}

    .q-tag {{
      font-size: 0.72rem;
      font-weight: 800;
      padding: 3px 10px;
      border-radius: 9999px;
      background-color: #eff6ff;
      color: #1d4ed8;
      border: 1px solid #bfdbfe;
      white-space: nowrap;
      flex-shrink: 0;
    }}

    .q-text {{
      font-size: 0.98rem;
      font-weight: 700;
      color: #1d4ed8;
      line-height: 1.4;
      flex: 1;
    }}

    .options-container {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .opt-item {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 12px;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
      background-color: #f8fafc;
      font-size: 0.88rem;
      position: relative;
    }}

    .opt-label {{
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background-color: #ffffff;
      border: 1px solid #cbd5e1;
      font-weight: 700;
      font-size: 0.8rem;
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

    .kw-green {{
      background-color: #d1fae5;
      color: #047857;
      font-weight: 800;
      padding: 1px 5px;
      border-radius: 4px;
      border: 1px solid #a7f3d0;
    }}

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
      font-size: 0.7rem;
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
      padding: 12px 16px;
      text-align: left;
      font-size: 0.88rem;
    }}

    .keyword-table th {{
      background-color: #eff6ff;
      color: #1e40af;
      font-weight: 800;
    }}

    .keyword-table td.q-col {{
      color: #1d4ed8;
      font-weight: 700;
      width: 40%;
    }}

    .keyword-table td.a-col {{
      color: #047857;
      font-weight: 700;
      width: 60%;
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

  <!-- ULTRA-THIN SLEEK 5 TABS HEADER BAR -->
  <nav class="tab-bar">
    <button class="tab-item active" data-sec="sec1">
      <i class="fa-solid fa-triangle-exclamation"></i>
      <span>1: Bẫy Tất Cả</span>
      <small>6 câu</small>
    </button>
    <button class="tab-item" data-sec="sec2">
      <i class="fa-solid fa-ruler"></i>
      <span>2: Đáp Án Dài Nhất</span>
      <small>44 câu</small>
    </button>
    <button class="tab-item" data-sec="sec3">
      <i class="fa-solid fa-key"></i>
      <span>3: Bảng Lỗ Hổng & Mẹo Khoanh</span>
      <small>Khoanh 0.5s</small>
    </button>
    <button class="tab-item" data-sec="sec4">
      <i class="fa-solid fa-circle-exclamation"></i>
      <span>4: Câu Bẫy Phủ Định</span>
      <small>25 câu</small>
    </button>
    <button class="tab-item" data-sec="sec5">
      <i class="fa-solid fa-layer-group"></i>
      <span>5: Các Câu Còn Lại</span>
      <small>242 câu</small>
    </button>
  </nav>

  <!-- TAB 1 CONTENT -->
  <div class="tab-content active" id="sec1">
    <div class="section">
      <div class="section-title">
        <i class="fa-solid fa-triangle-exclamation" style="color: #ef4444;"></i>
        PHẦN 1: DẠNG CÂU HỎI "TẤT CẢ ĐỀU ĐÚNG / TẤT CẢ..." (Toàn bộ {len(sec1_tricks) + len(sec1_rights)} câu)
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

for item, tat_ca_lbl, tat_ca_txt, correct, correct_txt in sec1_tricks:
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

for item, l, t in sec1_rights:
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
  </div>

  <!-- TAB 2 CONTENT -->
  <div class="tab-content" id="sec2">
    <div class="section">
      <div class="section-title">
        <i class="fa-solid fa-ruler" style="color: #2563eb;"></i>
        PHẦN 2: CÁC CÂU QUY TẮC "ĐÁP ÁN DÀI NHẤT" (Toàn bộ {len(sec2_rights) + len(sec2_tricks)} câu)
      </div>

      <div class="alert-box success">
        💡 <strong>QUY TẮC VÀNG:</strong> Các đáp án dài vượt trội có tỷ lệ đúng rất cao ({len(sec2_rights)} câu). Tuy nhiên có {len(sec2_tricks)} câu là bẫy dài nhất!
      </div>

      <div class="sub-heading success">
        <i class="fa-solid fa-check-double"></i>
        2.1. ĐẦY ĐỦ TOÀN BỘ {len(sec2_rights)} CÂU có Đáp án dài vượt trội là ĐÚNG CHUẨN:
      </div>
      <div class="q-grid">
"""

for item, l, t in sec2_rights:
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
        2.2. ĐẦY ĐỦ TOÀN BỘ {len(sec2_tricks)} CÂU BẪY DÀI NHẤT! (Dài nhất nhưng SAI - Khoanh câu khác):
      </div>
      <div class="q-grid">
"""

for item, longest_lbl, longest_txt, correct, correct_txt in sec2_tricks:
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
  </div>

  <!-- TAB 3 CONTENT: LỖ HỔNG CÂU HỎI & MẸO KHOANH TRONG 0.5 GIÂY -->
  <div class="tab-content" id="sec3">
    <div class="section">
      <div class="section-title">
        <i class="fa-solid fa-bolt" style="color: #d97706;"></i>
        PHẦN 3: BẢNG LỖ HỔNG CÂU HỎI & MẸO KHOANH SIÊU TỐC (NHÌN ĐỀ KHOANH NGAY TRONG 0.5S)
      </div>

      <div class="alert-box success">
        ⚡ <strong>MẸO LỖ HỔNG (LOOPHOLE SHORTCUTS):</strong> Dưới đây là 13 Dấu hiệu "Lỗ hổng" trực tiếp từ câu hỏi giúp bạn khoanh ngay lập tức mà không cần phân tích lý luận phức tạp!
      </div>

      <table class="keyword-table">
        <thead>
          <tr>
            <th>Dấu hiệu / Lỗ hổng trong CÂU HỎI (Màu Xanh Dương)</th>
            <th>Mẹo Khoanh / Từ khóa ĐÚNG CHUẨN Cần Khoanh (Highlight Xanh Lá)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="q-col">1. Đề hỏi <strong>"Hêghen"</strong> hoặc <strong>"Triết học Hêghen"</strong></td>
            <td class="a-col">Khoanh ngay <span class="kw-green">"Chủ nghĩa duy tâm khách quan"</span> hoặc <span class="kw-green">"Phép biện chứng"</span></td>
          </tr>
          <tr>
            <td class="q-col">2. Đề hỏi <strong>"Phoi-ơ-bắc" (L.Feuerbach)</strong></td>
            <td class="a-col">Khoanh ngay <span class="kw-green">"Chủ nghĩa duy vật siêu hình"</span> (hoặc chất phác)</td>
          </tr>
          <tr>
            <td class="q-col">3. Đề hỏi <strong>"Vật chất"</strong> hoặc <strong>"Định nghĩa Lênin"</strong> (29 câu)</td>
            <td class="a-col">Khoanh ngay <span class="kw-green">"Thực tại khách quan"</span> hoặc <span class="kw-green">"Tồn tại độc lập với ý thức"</span></td>
          </tr>
          <tr>
            <td class="q-col">4. Đề hỏi <strong>"Vận động"</strong> (9 câu)</td>
            <td class="a-col">Khoanh ngay <span class="kw-green">"Phương thức tồn tại của vật chất"</span> (tuyệt đối, vĩnh viễn)</td>
          </tr>
          <tr>
            <td class="q-col">5. Đề hỏi <strong>"Không gian và Thời gian"</strong> (4 câu)</td>
            <td class="a-col">Khoanh ngay <span class="kw-green">"Hình thức tồn tại của vật chất"</span></td>
          </tr>
          <tr>
            <td class="q-col">6. Đề hỏi <strong>"Ý thức"</strong> (15 câu)</td>
            <td class="a-col">Khoanh ngay <span class="kw-green">"Hình ảnh phản ánh tích cực, sáng tạo"</span> (mang tính chủ quan)</td>
          </tr>
          <tr>
            <td class="q-col">7. Đề hỏi <strong>"Thực tiễn"</strong> (13 câu)</td>
            <td class="a-col">Khoanh ngay <span class="kw-green">"Cơ sở, động lực, mục đích của nhận thức"</span></td>
          </tr>
          <tr>
            <td class="q-col">8. Đề hỏi <strong>"Tiền đề Khoa học Tự nhiên"</strong> / <strong>"Phát minh"</strong></td>
            <td class="a-col">Khoanh ngay bộ 3: <span class="kw-green">Thuyết tế bào</span>, <span class="kw-green">Bảo toàn năng lượng</span>, <span class="kw-green">Tiến hóa Đácuyn</span></td>
          </tr>
          <tr>
            <td class="q-col">9. Đề hỏi <strong>"Tiền đề lý luận trực tiếp"</strong></td>
            <td class="a-col">Khoanh ngay <span class="kw-green">"Triết học cổ điển Đức"</span></td>
          </tr>
          <tr>
            <td class="q-col">10. Đề hỏi mối quan hệ <strong>"Quyết định"</strong> (20 câu)</td>
            <td class="a-col">Áp dụng quy tắc: <strong>Thực thể Vật chất/Kinh tế/Hạ tầng</strong> luôn <span class="kw-green">QUYẾT ĐỊNH</span> <strong>Thực thể Ý thức/Chính trị/Thượng tầng</strong></td>
          </tr>
          <tr>
            <td class="q-col">11. Đề hỏi <strong>"Phương thức sản xuất"</strong> (5 câu)</td>
            <td class="a-col">Khoanh ngay <span class="kw-green">"Quyết định sự phát triển và biến đổi của xã hội"</span></td>
          </tr>
          <tr>
            <td class="q-col">12. Đề hỏi <strong>"Lực lượng sản xuất"</strong> (10 câu)</td>
            <td class="a-col">Khoanh ngay <span class="kw-green">"Yếu tố động nhất, cách mạng nhất"</span></td>
          </tr>
          <tr>
            <td class="q-col">13. Đề hỏi <strong>"Quần chúng nhân dân"</strong> (8 câu)</td>
            <td class="a-col">Khoanh ngay <span class="kw-green">"Lực lượng quyết định và sáng tạo ra lịch sử"</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- TAB 4 CONTENT -->
  <div class="tab-content" id="sec4">
    <div class="section">
      <div class="section-title">
        <i class="fa-solid fa-circle-exclamation" style="color: #6b7280;"></i>
        PHẦN 4: ĐẦY ĐỦ CÁC CÂU HỎI BẪY PHỦ ĐỊNH ("SAI", "KHÔNG ĐÚNG") - (Toàn bộ {len(sec4_qs)} câu)
      </div>

      <div class="alert-box">
        ⚠️ Khi đề bài hỏi <strong>"Nhận xét/Khẳng định nào SAI"</strong>, tuyệt đối không khoanh đáp án đúng! Hãy tìm câu phát biểu có từ <em>"tách rời"</em>, <em>"thống nhất ở ý thức"</em>, <em>"không có vai trò"</em> hoặc <em>"lắp ghép kết hợp"</em> để khoanh.
      </div>

      {render_grid_section(sec4_qs)}
    </div>
  </div>

  <!-- TAB 5 CONTENT -->
  <div class="tab-content" id="sec5">
    <div class="section">
      <div class="section-title">
        <i class="fa-solid fa-layer-group" style="color: #7c3aed;"></i>
        PHẦN 5: ĐẦY ĐỦ TOÀN BỘ CÁC CÂU HỎI CÒN LẠI PHÂN THEO NHÓM MẸO KHÁC (Toàn bộ {len(remaining_qs)} câu)
      </div>

      <div class="alert-box success">
        🎯 Phần này bao gồm toàn bộ {len(remaining_qs)} câu hỏi còn lại trong ngân hàng 331 câu, được phân nhóm theo 5 dạng kiến thức chuyên biệt để học thuộc lòng trong 5 phút!
      </div>

      <div class="sub-heading primary">
        <i class="fa-solid fa-brain"></i>
        5.1. Nhóm Mẹo VẬT CHẤT - Ý THỨC - THỰC TIỄN ({len(sec5_1)} câu):
      </div>
      <p style="font-size: 0.88rem; color: #475569; margin-bottom: 12px;">Mẹo: Luôn ưu tiên chọn đáp án chứa từ khóa <strong>"Thực tại khách quan"</strong>, <strong>"Vận động là phương thức tồn tại"</strong>, <strong>"Phản ánh"</strong>, <strong>"Tính tích cực sáng tạo"</strong>, <strong>"Thực tiễn quyết định nhận thức"</strong>.</p>
      {render_grid_section(sec5_1)}

      <div class="sub-heading primary">
        <i class="fa-solid fa-infinity"></i>
        5.2. Nhóm Mẹo PHÉP BIỆN CHỨNG DUY VẬT - QUY LUẬT & CẶP PHẠM TRÙ ({len(sec5_2)} câu):
      </div>
      <p style="font-size: 0.88rem; color: #475569; margin-bottom: 12px;">Mẹo: Ưu tiên đáp án khẳng định sự <strong>"Mối liên hệ phổ biến"</strong>, <strong>"Phát triển"</strong>, <strong>"Thống nhất của các mặt đối lập"</strong>, <strong>"Tích lũy về lượng dẫn đến thay đổi về chất"</strong>, <strong>"Cái chung tồn tại trong cái riêng"</strong>.</p>
      {render_grid_section(sec5_2)}

      <div class="sub-heading primary">
        <i class="fa-solid fa-earth-americas"></i>
        5.3. Nhóm Mẹo CHỦ NGHĨA DUY VẬT LỊCH SỬ - KINH TẾ & XÃ HỘI ({len(sec5_3)} câu):
      </div>
      <p style="font-size: 0.88rem; color: #475569; margin-bottom: 12px;">Mẹo: Nhớ nguyên lý <strong>"Phương thức sản xuất quyết định xã hội"</strong>, <strong>"Lực lượng sản xuất quyết định quan hệ sản xuất"</strong>, <strong>"Cơ sở hạ tầng quyết định kiến trúc thượng tầng"</strong>, <strong>"Tồn tại xã hội quyết định ý thức xã hội"</strong>.</p>
      {render_grid_section(sec5_3)}

      <div class="sub-heading primary">
        <i class="fa-solid fa-user-graduate"></i>
        5.4. Nhóm Mẹo TRIẾT GIA & LỊCH SỬ TRIẾT HỌC ({len(sec5_4)} câu):
      </div>
      <p style="font-size: 0.88rem; color: #475569; margin-bottom: 12px;">Mẹo: Hêghen (Duy tâm khách quan) • Phoiơbắc (Duy vật siêu hình) • Mác & Ăngghen (Sáng lập Duy vật biện chứng) • Lênin (Bổ sung phát triển giai đoạn TBCN độc quyền).</p>
      {render_grid_section(sec5_4)}

      <div class="sub-heading primary">
        <i class="fa-solid fa-list-check"></i>
        5.5. Nhóm CÂU HỎI TỔNG HỢP CÒN LẠI ({len(sec5_5)} câu):
      </div>
      {render_grid_section(sec5_5)}

    </div>
  </div>

  <!-- TAB SWITCHING SCRIPT -->
  <script>
    document.addEventListener('DOMContentLoaded', () => {{
      const tabItems = document.querySelectorAll('.tab-item');
      const tabContents = document.querySelectorAll('.tab-content');

      tabItems.forEach(item => {{
        item.addEventListener('click', () => {{
          tabItems.forEach(t => t.classList.remove('active'));
          tabContents.forEach(c => c.classList.remove('active'));

          item.classList.add('active');
          const secId = item.dataset.sec;
          const targetContent = document.getElementById(secId);
          if (targetContent) {{
            targetContent.classList.add('active');
          }}
        }});
      }});
    }});
  </script>

</body>
</html>
"""

with open('meo_hoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully generated meo_hoc.html with 13 Golden Question Loopholes in Tab 3!")
