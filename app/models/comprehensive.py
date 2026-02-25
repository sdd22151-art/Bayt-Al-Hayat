from pydantic import BaseModel, Field
from typing import List, Optional


class ComprehensiveAnswers(BaseModel):
    """Complete answers for all assessments"""
    
    name: str = Field(..., description="User name")
    
    psychology_answers: List[int] = Field(..., min_length=7, max_length=7)
    
    neuroscience_answers: List[str] = Field(..., min_length=9, max_length=9)
    
    birth_date: str = Field(..., description="YYYY-MM-DD format")
    day_type: str = Field(default="today", description="today/tomorrow/yesterday")
    birth_time: Optional[str] = Field(None, description="HH:MM format")
    birth_place: Optional[str] = Field(None, description="Birth location name")
    gender: Optional[str] = Field(None, description="male/female")
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ComprehensiveResult(BaseModel):
    """Complete assessment results"""
    
    psychology: dict
    neuroscience: dict
    astrology: dict
    video: dict
    status: str
    message: str
