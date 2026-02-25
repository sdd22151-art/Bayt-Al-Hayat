from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..models.comprehensive import ComprehensiveAnswers, ComprehensiveResult
from ..services.comprehensive_service import ComprehensiveService
from ..services.ai_video_service import AIVideoService

router = APIRouter(prefix="/comprehensive", tags=["comprehensive"])


@router.post("/submit", response_model=Dict[str, Any])
async def submit_comprehensive_answers(submission: ComprehensiveAnswers):
    """
    Submit all assessment answers and get comprehensive analysis
    
    Args:
        submission: All answers (psychology, neuroscience, astrology)
    
    Returns:
        Dict: Complete analysis combining all three assessments
    
    Raises:
        HTTPException: If validation or processing fails
    """
    try:
        result = await ComprehensiveService.analyze_all(
            name=submission.name,
            psychology_answers=submission.psychology_answers,
            neuroscience_answers=submission.neuroscience_answers,
            birth_date=submission.birth_date,
            birth_time=submission.birth_time,
            birth_place=submission.birth_place
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-video", response_model=Dict[str, Any])
async def generate_comprehensive_video(
    submission: ComprehensiveAnswers,
    model: str = "gpt4o",
    voice: str = "nova"
):
    """
    Generate AI video combining psychology, neuroscience, and astrology analysis
    
    Args:
        submission: Complete user data for all three assessments
        model: AI model for script generation (gpt4o, gpt4, gpt35)
        voice: Voice model for TTS (nova, alloy, shimmer)
    
    Returns:
        Dict with comprehensive analysis and video generation result
    
    Raises:
        HTTPException: If generation fails
    """
    try:
        video_data = await ComprehensiveService.analyze_all(
            name=submission.name,
            psychology_answers=submission.psychology_answers,
            neuroscience_answers=submission.neuroscience_answers,
            birth_date=submission.birth_date,
            birth_time=submission.birth_time,
            birth_place=submission.birth_place
        )
        
        video_result = await AIVideoService.generate_full_video(
            video_data,
            "videos/comprehensive",
            model=model,
            voice=voice
        )
        
        return {
            "analysis": video_data,
            "video": video_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive video generation failed: {str(e)}")
