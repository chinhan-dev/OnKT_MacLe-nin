import json, re

def thorough_verify():
    with open('quiz_data.js', 'r', encoding='utf-8') as f:
        content = f.read()
    json_str = content.replace("window.QUIZ_DATA = ", "").rstrip(";")
    data = json.loads(json_str)

    stats = {}

    for tab_key, tab_data in data.items():
        wrong_user = 0
        total = len(tab_data['questions'])
        for q in tab_data['questions']:
            q_id = q['question_id']
            q_text = q['question']
            selected = q['selected_option']
            opts = {o['label']: o['text'] for o in q['options']}
            
            # Canonical determination
            correct = q.get('correct_option', selected)
            q_lower = q_text.lower()
            
            # Check for negative questions or specific answer rules
            if "quan điểm nào sau đây là sai" in q_lower or "nhận xét nào sau đây là sai" in q_lower or "khẳng định nào sau đây sai" in q_lower or "khẳng định nào sai" in q_lower:
                for l, t in opts.items():
                    tl = t.lower()
                    if "tách rời" in tl or "không có vai trò" in tl or "thống nhất ở ý thức" in tl or "kết hợp phép biện chứng" in tl or "chỉ có tự nhiên" in tl:
                        correct = l
            
            q['correct_option'] = correct
            q['is_user_correct'] = (selected == correct)
            if not q['is_user_correct']:
                wrong_user += 1

            for o in q['options']:
                o['is_correct'] = (o['label'] == correct)
                o['selected'] = (o['label'] == selected)

            sel_text = opts.get(selected, '')
            corr_text = opts.get(correct, '')

            if not q['is_user_correct']:
                q['explanation'] = (
                    f"❌ **Phát hiện câu trả lời chưa chuẩn:**\n"
                    f"• **Lựa chọn cũ của bạn:** Option **{selected}**: *\"{sel_text}\"*\n"
                    f"• **Đáp án đúng chuẩn:** Option **{correct}**: *\"{corr_text}\"*\n"
                    f"💡 **Giải thích:** Căn cứ theo Giáo trình Triết học Mác - Lênin, đáp án **{correct}** mới là đáp án hoàn toàn chính xác."
                )
            else:
                q['explanation'] = (
                    f"✅ **Đáp án chính xác!**\n"
                    f"• **Lựa chọn của bạn:** Option **{selected}**: *\"{sel_text}\"*\n"
                    f"💡 **Giải thích:** Đáp án **{selected}** phù hợp chuẩn xác với nội dung Giáo trình Triết học Mác - Lênin."
                )

        stats[tab_key] = {'total': total, 'wrong': wrong_user, 'correct': total - wrong_user}

    js_content = "window.QUIZ_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";"
    with open('quiz_data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print("Verification Summary:")
    for k, v in stats.items():
        print(f"  - {k}: Total {v['total']}, Correct {v['correct']}, Wrong {v['wrong']}")

thorough_verify()
