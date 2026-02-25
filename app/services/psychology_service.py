from typing import List
from ..models.psychology import Question, QuestionnaireResponse, AssessmentResult


class PsychologyService:
    """Business logic service for psychology assessment"""
    
    QUESTIONS = [
        {
            "id": 1,
            "text": "كيف هو نومك؟",
            "options": [
                "مريح ومنتظم",
                "متقطع أحيانًا",
                "سيئ أو غير منتظم"
            ]
        },
        {
            "id": 2,
            "text": "إحساسك العام في يومك؟",
            "options": [
                "مرتاح ومتوازن",
                "محتمل",
                "مستنزف ومتعب"
            ]
        },
        {
            "id": 3,
            "text": "الإحساس المسيطر عليك مؤخرًا؟",
            "options": [
                "هدوء واطمئنان",
                "قلق أو توتر",
                "حزن أو ثِقل نفسي"
            ]
        },
        {
            "id": 4,
            "text": "قدرتك على الاستمتاع بالأشياء؟",
            "options": [
                "طبيعية",
                "أقل من المعتاد",
                "شبه معدومة"
            ]
        },
        {
            "id": 5,
            "text": "مستوى القلق أو التفكير الزائد؟",
            "options": [
                "قليل",
                "متوسط",
                "شديد ومزعج"
            ]
        },
        {
            "id": 6,
            "text": "طاقتك النفسية والجسدية؟",
            "options": [
                "جيدة",
                "متوسطة",
                "ضعيفة جدًا"
            ]
        },
        {
            "id": 7,
            "text": "نظرتك لنفسك؟",
            "options": [
                "إيجابية أو متوازنة",
                "متذبذبة",
                "سلبية أو قاسية على نفسي"
            ]
        }
    ]
    
    LEVEL_MESSAGES = {
        "حالة مستقرة": (
            "حالتك النفسية مستقرة بشكل عام. استمر في الحفاظ على نمط حياة صحي، "
            "ولا تتردد في طلب الدعم عند الحاجة."
        ),
        "ضغط نفسي خفيف": (
            "تمر بفترة من الضغط النفسي الخفيف. حاول أخذ فترات راحة، "
            "ومارس أنشطة تساعدك على الاسترخاء مثل المشي أو التأمل. "
            "إذا استمرت الحالة، يُنصح باستشارة متخصص."
        ),
        "اضطراب مزاجي متوسط": (
            "تشير النتيجة إلى وجود اضطراب مزاجي متوسط. "
            "يُنصح بشدة بالتحدث مع أخصائي نفسي أو معالج للحصول على الدعم المناسب. "
            "لا تتردد في طلب المساعدة، فهي خطوة إيجابية نحو التحسن."
        ),
        "اضطراب مزاجي مرتفع – يُنصح بتقييم متخصص": (
            "النتيجة تشير إلى اضطراب مزاجي مرتفع. "
            "من المهم جدًا أن تطلب مساعدة متخصصة في أقرب وقت ممكن. "
            "تواصل مع أخصائي نفسي أو طبيب نفسي لتقييم شامل ووضع خطة علاجية مناسبة. "
            "صحتك النفسية أولوية."
        )
    }
    
    @classmethod
    def get_questionnaire(cls) -> QuestionnaireResponse:
        """Return complete questionnaire with all questions"""
        questions = [Question(**q) for q in cls.QUESTIONS]
        
        return QuestionnaireResponse(
            title="تقييم الحالة النفسية",
            description="اختر الإجابة الأقرب لك خلال الأسبوع الأخير",
            questions=questions
        )
    
    @classmethod
    def calculate_assessment(cls, answers: List[int]) -> AssessmentResult:
        """Calculate result and determine level with appropriate message"""
        score = sum(answers)
        
        if 7 <= score <= 10:
            level = "حالة مستقرة"
        elif 11 <= score <= 14:
            level = "ضغط نفسي خفيف"
        elif 15 <= score <= 18:
            level = "اضطراب مزاجي متوسط"
        else:
            level = "اضطراب مزاجي مرتفع – يُنصح بتقييم متخصص"
        
        message = cls.LEVEL_MESSAGES[level]
        
        supportive_messages = []
        
        if answers[0] >= 2:
            supportive_messages.append(
                "النوم الجيد أساس صحتك النفسية. حاول تهيئة بيئة نوم هادئة، "
                "وتجنب الشاشات قبل النوم بساعة على الأقل."
            )
        
        if answers[2] >= 2:
            supportive_messages.append(
                "القلق والتوتر طبيعيان، لكن يمكن التحكم بهما. "
                "جرّب تمارين التنفس العميق أو المشي في الطبيعة."
            )
        
        if answers[4] >= 2:
            supportive_messages.append(
                "التفكير الزائد مرهق. حاول كتابة أفكارك أو التحدث مع شخص تثق به. "
                "لا تحمل كل شيء بمفردك."
            )
        
        if answers[6] >= 2:
            supportive_messages.append(
                "نظرتك لنفسك مهمة جدًا. تذكر إنجازاتك ونقاط قوتك. "
                "أنت أفضل مما تظن، وتستحق الحب والتقدير."
            )
        
        return AssessmentResult(
            score=score,
            level=level,
            message=message,
            supportive_messages=supportive_messages
        )
