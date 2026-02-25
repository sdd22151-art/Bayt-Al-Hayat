from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Literal, Optional


class AstrologyRequest(BaseModel):
    """نموذج طلب تحليل برج اليوم"""
    name: str = Field(default="", description="اسم المستخدم (اختياري)")
    birth_date: str = Field(..., description="تاريخ الميلاد بصيغة YYYY-MM-DD")
    birth_time: Optional[str] = Field(default=None, description="وقت الميلاد HH:MM (اختياري للطالع)")
    birth_location: str = Field(default="", description="مكان الميلاد (اختياري)")
    latitude: Optional[float] = Field(default=None, description="خط العرض (اختياري)")
    longitude: Optional[float] = Field(default=None, description="خط الطول (اختياري)")
    day_type: Literal["today", "tomorrow", "yesterday"] = Field(
        default="today", 
        description="نوع اليوم المطلوب تحليله"
    )
    
    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: str) -> str:
        """التحقق من تاريخ الميلاد"""
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError('تاريخ الميلاد يجب أن يكون بصيغة YYYY-MM-DD')


class AstrologyResponse(BaseModel):
    """نموذج نتيجة تحليل البرج اليومي"""
    name: str = Field(default="", description="الاسم")
    sun_sign: str = Field(..., description="البرج الشمسي")
    ascendant: str = Field(default="", description="الطالع")
    birth_date: str
    day_type: str
    psychological_state: str = Field(..., description="الحالة النفسية")
    emotional_state: str = Field(..., description="الحالة العاطفية")
    mental_state: str = Field(..., description="الحالة الذهنية")
    physical_state: str = Field(..., description="الحالة الجسدية")
    luck_level: str = Field(..., description="مستوى الحظ")
    lucky_color: str = Field(..., description="اللون المحظوظ")
    lucky_number: str = Field(..., description="الرقم المحظوظ")
    compatibility: str = Field(..., description="التوافق")
    advice: str = Field(..., description="النصيحة")
    warning: str = Field(..., description="التحذير")
