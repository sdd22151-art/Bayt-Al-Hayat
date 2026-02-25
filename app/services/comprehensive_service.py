from typing import Dict, Any
from ..services.psychology_service import PsychologyService
from ..services.neuroscience_service import NeuroscienceService
from ..services.astrology_service import AstrologyService
from ..models.astrology import AstrologyRequest


class ComprehensiveService:
    """Service for comprehensive multi-assessment analysis"""
    
    @classmethod
    async def analyze_all(
        cls,
        name: str,
        psychology_answers: list,
        neuroscience_answers: list,
        birth_date: str,
        day_type: str = "today",
        birth_time: str = None,
        birth_place: str = None,
        latitude: float = None,
        longitude: float = None
    ) -> Dict[str, Any]:
        
        psychology_result = PsychologyService.calculate_assessment(psychology_answers)
        
        neuroscience_result = NeuroscienceService.calculate_assessment(neuroscience_answers)
        
        astrology_request = AstrologyRequest(
            name=name,
            birth_date=birth_date,
            day_type=day_type,
            birth_time=birth_time,
            birth_location=birth_place or "",
            latitude=latitude,
            longitude=longitude
        )
        astrology_result = await AstrologyService.analyze(astrology_request)
        
        comprehensive_data = {
            "name": name,
            "type": "comprehensive",
            
            "psychology": {
                "score": psychology_result.score,
                "level": psychology_result.level,
                "message": psychology_result.message,
                "supportive_messages": psychology_result.supportive_messages
            },
            
            "neuroscience": {
                "dominant": neuroscience_result.dominant,
                "secondary": neuroscience_result.secondary,
                "strong_secondary": neuroscience_result.strong_secondary,
                "description": neuroscience_result.description,
                "scores": {
                    "Fight": neuroscience_result.scores.A,
                    "Flight": neuroscience_result.scores.B,
                    "Freeze": neuroscience_result.scores.C,
                    "Fawn": neuroscience_result.scores.D
                }
            },
            
            "astrology": {
                "sun_sign": astrology_result.sun_sign,
                "ascendant": astrology_result.ascendant,
                "psychological_state": astrology_result.psychological_state,
                "emotional_state": astrology_result.emotional_state,
                "mental_state": astrology_result.mental_state,
                "physical_state": astrology_result.physical_state,
                "luck_level": astrology_result.luck_level,
                "lucky_color": astrology_result.lucky_color,
                "lucky_number": astrology_result.lucky_number,
                "compatibility": astrology_result.compatibility,
                "advice": astrology_result.advice,
                "warning": astrology_result.warning
            }
        }
        
        return comprehensive_data
