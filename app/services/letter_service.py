import math
from typing import Tuple
from ..models.letter import LetterAnalysisRequest, LetterAnalysisResponse, GuidanceDictionary


class LetterService:
    """خدمة منطق الأعمال لعلم الحرف"""
    

    SPIRITUAL_GUIDANCE = {
        "ل": "توطيد العلاقة مع الله",
        "س": "التركيز على التسبيح",
        "ح": "التركيز على التسبيح",
        "ي": "التركيز على التسبيح",
        "ن": "زيادة الصبر",
        "م": "زيادة الصوم",
        "ص": "زيادة الصوم",
        "ط": "زيادة الطهارة"
    }
    

    BEHAVIORAL_GUIDANCE = {
        "أ": "زيادة الود واللطف",
        "ء": "زيادة الود واللطف",
        "ب": "التشافي من الماضي",
        "ت": "التشافي من الماضي",
        "ج": "السكون والهدوء",
        "ث": "السكون والهدوء",
        "خ": "السكون والهدوء",
        "ك": "السكون والهدوء",
        "ع": "تكثيف التعلم",
        "ر": "تكثيف التعلم",
        "غ": "تكثيف التعلم",
        "ض": "زيادة التعامل الاجتماعي",
        "ظ": "زيادة التعامل الاجتماعي",
        "ش": "تقليل الظهور",
        "ز": "تقليل الظهور"
    }
    

    PHYSICAL_GUIDANCE = {
        "هـ": "زيادة الرياضة والتنفس",
        "ه": "زيادة الرياضة والتنفس",
        "و": "زيادة الرياضة والتنفس",
        "ف": "زيادة الحركة",
        "ق": "زيادة الحركة"
    }
    

    DEPENDENT_LETTERS = ["د", "ذ"]
    
    @classmethod
    def clean_name(cls, name: str) -> str:
        """تنظيف الاسم: إزالة المسافات والاحتفاظ بالحروف فقط"""

        cleaned = name.replace(" ", "").strip()
        return cleaned
    
    @classmethod
    def calculate_stage_and_letter(cls, name: str, age: int) -> Tuple[int, str, int]:
        """
        حساب المرحلة والحرف الحاكم
        
        Returns:
            Tuple[int, str, int]: (stage, governing_letter, letters_count)
        """

        cleaned_name = cls.clean_name(name)
        letters_count = len(cleaned_name)
        

        if letters_count == 1:
            return 1, cleaned_name[0], letters_count
        

        if letters_count == 2:

            duration_per_letter = 20
            stage = min(math.ceil(age / duration_per_letter), letters_count)
            governing_letter = cleaned_name[stage - 1]
            return stage, governing_letter, letters_count
        

        if age < 20:
            stage = 1
        else:
            years_after_20 = age - 20
            stage = math.ceil(years_after_20 / 15) + 1
        

        if stage > letters_count:
            duration_per_letter = age / letters_count
            stage = math.ceil(age / duration_per_letter)
            stage = min(stage, letters_count)
        
        governing_letter = cleaned_name[stage - 1]
        return stage, governing_letter, letters_count
    
    @classmethod
    def apply_dependency_rule(cls, governing_letter: str, name: str, stage: int) -> Tuple[str, bool]:
        """
        تطبيق قاعدة التبعية
        
        Returns:
            Tuple[str, bool]: (final_letter, is_dependent)
        """
        if governing_letter in cls.DEPENDENT_LETTERS:

            if stage > 1:
                cleaned_name = cls.clean_name(name)
                previous_letter = cleaned_name[stage - 2]
                return previous_letter, True
            else:

                return governing_letter, True
        
        return governing_letter, False
    
    @classmethod
    def get_guidance(cls, letter: str) -> Tuple[str, str]:
        """
        الحصول على التوجيه المناسب للحرف
        
        Returns:
            Tuple[str, str]: (guidance_type, guidance_text)
        """

        if letter in cls.SPIRITUAL_GUIDANCE:
            return "spiritual", cls.SPIRITUAL_GUIDANCE[letter]
        

        if letter in cls.BEHAVIORAL_GUIDANCE:
            return "behavioral", cls.BEHAVIORAL_GUIDANCE[letter]
        

        if letter in cls.PHYSICAL_GUIDANCE:
            return "physical", cls.PHYSICAL_GUIDANCE[letter]
        

        return "dependent", f"لا يوجد توجيه محدد للحرف '{letter}'"
    
    @classmethod
    def analyze(cls, request: LetterAnalysisRequest) -> LetterAnalysisResponse:
        """
        تحليل الاسم والعمر وإرجاع التوجيه المناسب
        """

        stage, governing_letter, letters_count = cls.calculate_stage_and_letter(
            request.name, 
            request.age
        )
        

        final_letter, is_dependent = cls.apply_dependency_rule(
            governing_letter, 
            request.name, 
            stage
        )
        

        guidance_type, guidance = cls.get_guidance(final_letter)
        

        return LetterAnalysisResponse(
            name=request.name,
            age=request.age,
            letters_count=letters_count,
            stage=stage,
            governing_letter=final_letter,
            is_dependent=is_dependent,
            guidance_type=guidance_type,
            guidance=guidance
        )
    
    @classmethod
    def get_dictionary(cls) -> GuidanceDictionary:
        """إرجاع قاموس التوجيهات الكامل"""
        return GuidanceDictionary(
            spiritual=cls.SPIRITUAL_GUIDANCE,
            behavioral=cls.BEHAVIORAL_GUIDANCE,
            physical=cls.PHYSICAL_GUIDANCE
        )
