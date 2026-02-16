from pydantic import BaseModel, Field, field_validator
from typing import List


class Question(BaseModel):
    """نموذج السؤال"""
    id: int
    text: str
    options: List[str] = Field(..., min_length=3, max_length=3)


class QuestionnaireResponse(BaseModel):
    """نموذج الاستبيان الكامل"""
    title: str
    description: str
    questions: List[Question]


class AnswersSubmission(BaseModel):
    """نموذج إرسال الإجابات"""
    answers: List[int] = Field(..., min_length=7, max_length=7)
    
    @field_validator('answers')
    @classmethod
    def validate_answers(cls, v: List[int]) -> List[int]:
        """التحقق من أن جميع الإجابات بين 1 و 3"""
        for i, answer in enumerate(v, 1):
            if answer < 1 or answer > 3:
                raise ValueError(f'الإجابة رقم {i} يجب أن تكون بين 1 و 3، القيمة المدخلة: {answer}')
        return v


class AssessmentResult(BaseModel):
    """نموذج نتيجة التقييم"""
    score: int
    level: str
    message: str
