from fastapi import APIRouter, HTTPException
from ..models.letter import LetterAnalysisRequest, LetterAnalysisResponse, GuidanceDictionary
from ..services.letter_service import LetterService

router = APIRouter(prefix="/letter", tags=["letter"])


@router.post("/analyze", response_model=LetterAnalysisResponse)
async def analyze_letter(request: LetterAnalysisRequest):
    """
    تحليل الاسم والعمر وحساب الحرف الحاكم والتوجيه المناسب
    
    Args:
        request: الاسم والعمر
    
    Returns:
        LetterAnalysisResponse: نتيجة التحليل مع التوجيه المناسب
    
    Raises:
        HTTPException: في حالة وجود خطأ في التحليل
    """
    try:
        result = LetterService.analyze(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dictionary", response_model=GuidanceDictionary)
async def get_guidance_dictionary():
    """
    جلب قاموس التوجيهات الكامل (spiritual, behavioral, physical)
    
    Returns:
        GuidanceDictionary: قاموس التوجيهات الكامل
    """
    return LetterService.get_dictionary()
