from typing import Dict, Any, List
from pathlib import Path
import json
from datetime import datetime
import pandas as pd


class VideoAnalytics:
    
    ANALYTICS_DIR = Path("analytics")
    
    @classmethod
    def log_generation(
        cls,
        session_id: str,
        metadata: Dict[str, Any],
        performance_metrics: Dict[str, float]
    ) -> None:
        
        cls.ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "metadata": metadata,
            "performance": performance_metrics
        }
        
        log_file = cls.ANALYTICS_DIR / "generation_log.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        
        log_file = cls.ANALYTICS_DIR / "generation_log.jsonl"
        
        if not log_file.exists():
            return {"total_generations": 0}
        
        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                logs.append(json.loads(line))
        
        if not logs:
            return {"total_generations": 0}
        
        df = pd.DataFrame(logs)
        
        stats = {
            "total_generations": len(logs),
            "models_used": df['metadata'].apply(lambda x: x.get('model')).value_counts().to_dict(),
            "voices_used": df['metadata'].apply(lambda x: x.get('voice')).value_counts().to_dict(),
            "avg_script_length": df['metadata'].apply(lambda x: x.get('script_length', 0)).mean(),
            "cache_hit_rate": df['metadata'].apply(lambda x: x.get('cache_hit', False)).mean(),
            "recent_sessions": logs[-10:]
        }
        
        return stats
    
    @classmethod
    def analyze_quality(cls, script: str) -> Dict[str, Any]:
        
        words = script.split()
        sentences = script.split('.')
        
        quality_metrics = {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_sentence_length": len(words) / max(len(sentences), 1),
            "readability_score": cls._calculate_readability(script),
            "emotional_tone": cls._analyze_tone(script),
            "key_topics": cls._extract_topics(script)
        }
        
        return quality_metrics
    
    @classmethod
    def _calculate_readability(cls, text: str) -> float:
        words = text.split()
        sentences = text.split('.')
        
        if len(sentences) == 0:
            return 0.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        readability = 100 - (avg_words_per_sentence * 2)
        
        return max(0, min(100, readability))
    
    @classmethod
    def _analyze_tone(cls, text: str) -> str:
        positive_words = ['سعيد', 'جيد', 'ممتاز', 'رائع', 'قوي', 'نجاح', 'فرصة']
        negative_words = ['صعب', 'ضعيف', 'تحذير', 'حذر', 'مشكلة']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count * 1.5:
            return "positive"
        elif negative_count > positive_count:
            return "cautious"
        else:
            return "balanced"
    
    @classmethod
    def _extract_topics(cls, text: str) -> List[str]:
        topic_keywords = {
            "emotions": ['عاطفي', 'مشاعر', 'حب', 'علاقة'],
            "career": ['عمل', 'مهنة', 'نجاح', 'هدف'],
            "health": ['صحة', 'طاقة', 'جسد', 'راحة'],
            "relationships": ['علاقات', 'صداقة', 'عائلة', 'شريك']
        }
        
        topics = []
        text_lower = text.lower()
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
