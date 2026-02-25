from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..models.psychology import QuestionnaireResponse, AnswersSubmission, AssessmentResult
from ..services.psychology_service import PsychologyService
from ..services.ai_video_service import AIVideoService

router = APIRouter(prefix="/psychology", tags=["psychology"])


@router.get("", response_model=QuestionnaireResponse)
async def get_psychology_questionnaire():
    """
    Get psychology assessment questionnaire
    
    Returns:
        QuestionnaireResponse: Complete questionnaire with all questions
    """
    return PsychologyService.get_questionnaire()


@router.post("/submit", response_model=AssessmentResult)
async def submit_psychology_answers(submission: AnswersSubmission):
    """
    Submit user answers and calculate result
    
    Args:
        submission: User answers (7 answers, each between 1 and 3)
    
    Returns:
        AssessmentResult: Final result with level and message
    
    Raises:
        HTTPException: If validation fails
    """
    try:
        result = PsychologyService.calculate_assessment(submission.answers)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-video", response_model=Dict[str, Any])
async def generate_psychology_video(
    submission: AnswersSubmission,
    name: str = "Friend",
    model: str = "gpt4o",
    voice: str = "nova"
):
    """
    Generate AI video explaining psychology assessment results
    
    Args:
        submission: User answers
        name: User name for personalization
        model: AI model (gpt4o, gpt4, gpt35)
        voice: Voice model (nova, alloy, shimmer)
    
    Returns:
        Dict with assessment and video generation result
    """
    try:
        assessment = PsychologyService.calculate_assessment(submission.answers)
        
        video_data = {
            "name": name,
            "type": "psychology",
            "score": assessment.score,
            "level": assessment.level,
            "message": assessment.message,
            "supportive_messages": assessment.supportive_messages,
            "answers": submission.answers
        }
        
        video_result = await AIVideoService.generate_full_video(
            video_data, 
            "videos/psychology",
            model=model,
            voice=voice
        )
        
        return {
            "assessment": assessment.model_dump(),
            "video": video_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")
