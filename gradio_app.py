import gradio as gr
from app.services.psychology_service import PsychologyService

# جلب الأسئلة
questionnaire = PsychologyService.get_questionnaire()
questions = questionnaire.questions


def process_answers(*answers):
    """معالجة الإجابات وحساب النتيجة"""
    try:
        # تحويل الإجابات من النصوص إلى أرقام (1, 2, 3)
        numeric_answers = []
        for i, answer in enumerate(answers):
            if answer:
                # البحث عن الخيار في القائمة
                options = questions[i].options
                numeric_answer = options.index(answer) + 1
                numeric_answers.append(numeric_answer)
            else:
                return "⚠️ يرجى الإجابة على جميع الأسئلة"
        
        # التحقق من عدد الإجابات
        if len(numeric_answers) != 7:
            return "⚠️ يرجى الإجابة على جميع الأسئلة السبعة"
        
        # حساب النتيجة
        result = PsychologyService.calculate_assessment(numeric_answers)
        
        # تنسيق النتيجة
        output = f"""
## 📊 نتيجة التقييم

**الدرجة:** {result.score} / 21

**المستوى:** {result.level}

---

### 💬 الرسالة:

{result.message}

---

**تفاصيل إجاباتك:**
"""
        for i, (q, ans) in enumerate(zip(questions, numeric_answers), 1):
            output += f"\n{i}. {q.text}\n   ✓ {q.options[ans-1]}\n"
        
        return output
        
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"


# بناء الواجهة
with gr.Blocks(title="تقييم الحالة النفسية", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown(
        f"""
        # 🧠 {questionnaire.title}
        
        ### {questionnaire.description}
        
        ---
        """
    )
    
    # إنشاء قوائم منسدلة للأسئلة
    answer_components = []
    
    for q in questions:
        with gr.Group():
            gr.Markdown(f"### السؤال {q.id}: {q.text}")
            radio = gr.Radio(
                choices=q.options,
                label="اختر إجابتك",
                interactive=True
            )
            answer_components.append(radio)
    
    # زر الإرسال
    submit_btn = gr.Button("📝 إرسال الإجابات وعرض النتيجة", variant="primary", size="lg")
    
    # منطقة عرض النتيجة
    gr.Markdown("---")
    output = gr.Markdown(label="النتيجة")
    
    # ربط الزر بالوظيفة
    submit_btn.click(
        fn=process_answers,
        inputs=answer_components,
        outputs=output
    )
    
    gr.Markdown(
        """
        ---
        
        ### 📌 ملاحظات:
        
        - جميع الأسئلة إلزامية
        - اختر الإجابة الأقرب لحالتك خلال الأسبوع الأخير
        - النتائج توجيهية وليست تشخيصاً طبياً
        
        **تم التطوير بواسطة FastAPI + Gradio** ✨
        """
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=8000,
        share=False
    )
