from fastapi import APIRouter, HTTPException
from ..models.psychology import QuestionnaireResponse, AnswersSubmission, AssessmentResult
from ..services.psychology_service import PsychologyService

router = APIRouter(prefix="/psychology", tags=["psychology"])


@router.get("", response_model=QuestionnaireResponse)
async def get_psychology_questionnaire():
    """
    جلب استبيان تقييم الحالة النفسية
    
    Returns:
        QuestionnaireResponse: الاستبيان الكامل مع جميع الأسئلة
    """
    return PsychologyService.get_questionnaire()


@router.post("/submit", response_model=AssessmentResult)
async def submit_psychology_answers(submission: AnswersSubmission):
    """
    استقبال إجابات المستخدم وحساب النتيجة
    
    Args:
        submission: الإجابات المرسلة من المستخدم (7 إجابات، كل منها بين 1 و 3)
    
    Returns:
        AssessmentResult: النتيجة النهائية مع المستوى والرسالة المناسبة
    
    Raises:
        HTTPException: في حالة وجود خطأ في التحقق من صحة البيانات
    """
    try:
        result = PsychologyService.calculate_assessment(submission.answers)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
