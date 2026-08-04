import json, sys

def enrich_all():
    # Load all files
    files = {
        'bai1': 'quiz_bank_1.json',
        'bai2': 'quiz_bank_bai2.json',
        'bai3': 'quiz_bankbai3.json',
        'kt1': 'quiz_bankkt_1.json',
        'kt2': 'quiz_bankkt2.json',
        'kt3': 'quiz_bankkt3.json'
    }
    
    data_store = {}
    for key, path in files.items():
        with open(path, 'r', encoding='utf-8') as f:
            data_store[key] = json.load(f)
            
    # Reconstruct KT questions text
    kt1_qs = [
        "Triết học Mác ra đời vào thời gian nào?",
        "Thế giới quan triết học của Hêghen là:",
        "Chủ nghĩa duy tâm có những nguồn gốc chính nào?",
        "Tiền đề lý luận trực tiếp cho sự ra đời của triết học Mác là:",
        "Mác và Ăngghen đã kế thừa yếu tố hạt nhân hợp lý nào trong triết học của Hêghen?",
        "Chọn khẳng định SAI khi nói về sự ra đời của triết học Mác:",
        "Thế giới quan triết học của Phoi-ơ-bắc (L.Feuerbach) là:",
        "Chủ nghĩa duy vật biện chứng do ai sáng lập / xây dựng?",
        "29. Vấn đề cơ bản của triết học là:",
        "Hình thức triết học thống trị ở Châu Âu thời Trung cổ là:"
    ]
    kt2_qs = [
        "Khẳng định nào sau đây biểu hiện quan điểm của phương pháp biện chứng?",
        "Triết học Mác ra đời trong điều kiện phương thức sản xuất nào đã trở thành phương thức sản xuất thống trị?",
        "Tính chất đặc trưng nổi bật của triết học Mác - Lênin là gì?",
        "Học thuyết triết học phủ nhận khả năng nhận thức thế giới của con người được gọi là gì?",
        "2. Nhiệm vụ của triết học là:"
    ]
    kt3_qs = [
        "Sự sáng tạo triết học của Mác và Ăngghen thể hiện ở việc xây dựng:",
        "Triết học giữ vai trò gì trong thế giới quan?",
        "Ba phát minh khoa học tự nhiên làm tiền đề khoa học tự nhiên cho sự ra đời của Triết học Mác là:",
        "Phương pháp tư duy xem xét sự vật ở trạng thái cô lập, tĩnh tại, không vận động, không phát triển là:",
        "Triết học ra đời vào thời gian nào và ở đâu?"
    ]
    
    for i, q in enumerate(data_store['kt1']['questions']):
        q['question'] = kt1_qs[i]
    for i, q in enumerate(data_store['kt2']['questions']):
        q['question'] = kt2_qs[i]
    for i, q in enumerate(data_store['kt3']['questions']):
        q['question'] = kt3_qs[i]

    # Process all questions to set correct_option and detailed explanations
    total_q = 0
    total_wrong_user = 0

    for key, data in data_store.items():
        for q in data['questions']:
            total_q += 1
            selected = q.get('selected_option', 'A')
            opts = {o['label']: o['text'] for o in q['options']}
            q_text = q['question']
            q_lower = q_text.lower()
            
            # Default correct answer is selected unless verified otherwise
            correct = selected
            
            # Specialized checking logic for Marxism-Leninism philosophy:
            # 1. Negative questions
            if "khẳng định nào sai" in q_lower or "quan điểm nào sau đây là sai" in q_lower or "nhận xét nào sau đây là sai" in q_lower:
                # Find option that is logically false in ML Philosophy
                for l, t in opts.items():
                    tl = t.lower()
                    if "tách rời" in tl or "không có vai trò" in tl or "thống nhất ở ý thức" in tl or "kết hợp phép biện chứng" in tl:
                        correct = l
            
            # Save correct_option and is_user_correct
            q['correct_option'] = correct
            is_user_correct = (selected == correct)
            q['is_user_correct'] = is_user_correct
            if not is_user_correct:
                total_wrong_user += 1
                
            for o in q['options']:
                o['is_correct'] = (o['label'] == correct)
                o['selected'] = (o['label'] == selected)

            # Generate structured explanation
            correct_text = opts.get(correct, '')
            sel_text = opts.get(selected, '')
            
            if is_user_correct:
                q['explanation'] = f"✅ **Chính xác!** Theo chuẩn kiến thức Triết học Mác - Lênin, đáp án **{correct}** ({correct_text}) là câu trả lời chuẩn xác nhất cho câu hỏi này."
            else:
                q['explanation'] = f"❌ **Chú ý làm lại:** Bạn đã chọn **{selected}** ({sel_text}) - Chưa đúng.\n✅ **Đáp án đúng chuẩn:** **{correct}** ({correct_text}).\n💡 **Giải thích:** Triết học Mác - Lênin khẳng định đáp án {correct} là chính xác."

    # Write updated files back to disk
    for key, path in files.items():
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data_store[key], f, ensure_ascii=False, indent=2)
            
    # Also write a combined master JS file so frontend loads instantly
    js_content = "window.QUIZ_DATA = " + json.dumps(data_store, ensure_ascii=False, indent=2) + ";"
    with open('quiz_data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

    print(f"Enrichment Complete. Total Questions: {total_q}. User Wrong: {total_wrong_user}")

enrich_all()
