from pydantic import BaseModel, Field, field_validator
from typing import Literal


class LetterAnalysisRequest(BaseModel):
    """نموذج طلب تحليل علم الحرف"""
    name: str = Field(..., min_length=1, description="الاسم العربي")
    age: int = Field(..., gt=0, description="العمر (يجب أن يكون أكبر من 0)")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """التحقق من أن الاسم غير فارغ بعد إزالة المسافات"""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError('الاسم لا يمكن أن يكون فارغًا')
        return v
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v: int) -> int:
        """التحقق من أن العمر موجب"""
        if v <= 0:
            raise ValueError('العمر يجب أن يكون أكبر من صفر')
        return v


class LetterAnalysisResponse(BaseModel):
    """نموذج نتيجة تحليل علم الحرف"""
    name: str
    age: int
    letters_count: int
    stage: int
    governing_letter: str
    is_dependent: bool = False
    guidance_type: Literal["spiritual", "behavioral", "physical", "dependent"]
    guidance: str


class GuidanceDictionary(BaseModel):
    """نموذج قاموس التوجيهات"""
    spiritual: dict[str, str]
    behavioral: dict[str, str]
    physical: dict[str, str]
