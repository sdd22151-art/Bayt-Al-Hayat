import httpx
from typing import Dict, Any, Optional, List, Literal
from openai import AsyncOpenAI, OpenAI
import os
from pathlib import Path
import asyncio
import json
import hashlib
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)


class AIVideoService:
    
    @classmethod
    def _reload_env(cls):
        """Reload .env so updated keys take effect without restart."""
        load_dotenv(override=True)
    
    @classmethod
    def _get_openai_client(cls):
        cls._reload_env()
        return AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
    
    @classmethod
    def _get_did_key(cls):
        cls._reload_env()
        return os.getenv("D_ID_API_KEY", "")
    
    @classmethod
    def _get_runway_key(cls):
        cls._reload_env()
        return os.getenv("RUNWAY_API_KEY", "")
    
    @classmethod
    def _get_stability_key(cls):
        cls._reload_env()
        return os.getenv("STABILITY_API_KEY", "")
    
    @classmethod
    def _get_elevenlabs_key(cls):
        cls._reload_env()
        return os.getenv("ELEVENLABS_API_KEY", "")
    
    CACHE_DIR = Path("cache/scripts")
    OUTPUT_DIR = Path("videos")
    
    MODELS = {
        "gpt4": "gpt-4-turbo-preview",
        "gpt4o": "gpt-4o",
        "gpt35": "gpt-3.5-turbo"
    }
    
    MODEL_MAPPING = {
        "gpt4": "gpt-4-turbo-preview",
        "gpt4o": "gpt-4o",
        "gpt35": "gpt-3.5-turbo"
    }
    
    VOICES = {
        "alloy": {"name": "Alloy", "gender": "neutral", "lang": "ar"},
        "echo": {"name": "Echo", "gender": "male", "lang": "ar"},
        "fable": {"name": "Fable", "gender": "neutral", "lang": "ar"},
        "onyx": {"name": "Onyx", "gender": "male", "lang": "ar"},
        "nova": {"name": "Nova", "gender": "female", "lang": "ar"},
        "shimmer": {"name": "Shimmer", "gender": "female", "lang": "ar"}
    }
    
    # D-ID Microsoft Azure voices for Arabic
    DID_VOICE_MAPPING = {
        "nova":    "ar-SA-ZariyahNeural",     # female Arabic (Saudi)
        "alloy":   "ar-EG-ShakirNeural",      # male Arabic (Egypt)
        "echo":    "ar-SA-HamedNeural",       # male Arabic (Saudi)
        "fable":   "ar-EG-SalmaNeural",       # female Arabic (Egypt)
        "onyx":    "ar-SA-HamedNeural",       # male Arabic (Saudi)
        "shimmer": "ar-EG-SalmaNeural",       # female Arabic (Egypt)
    }
    
    AVATAR_PRESETS = {
        "arabic_male":   "https://d-id-public-bucket.s3.amazonaws.com/alice.jpg",
        "arabic_female": "https://d-id-public-bucket.s3.amazonaws.com/alice.jpg"
    }
    
    @classmethod
    def _get_cache_key(cls, data: Dict[str, Any]) -> str:
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    @classmethod
    async def _get_cached_script(cls, cache_key: str) -> Optional[str]:
        cache_file = cls.CACHE_DIR / f"{cache_key}.txt"
        if cache_file.exists():
            return cache_file.read_text(encoding='utf-8')
        return None
    
    @classmethod
    async def _cache_script(cls, cache_key: str, script: str) -> None:
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = cls.CACHE_DIR / f"{cache_key}.txt"
        cache_file.write_text(script, encoding='utf-8')
    
    @classmethod
    async def generate_script(
        cls, 
        astrology_result: Dict[str, Any],
        model: str = "gpt4o",
        temperature: float = 0.8,
        max_tokens: int = 2000,
        use_cache: bool = True
    ) -> str:
        
        cache_key = cls._get_cache_key({
            "data": astrology_result,
            "model": model,
            "type": "script"
        })
        
        if use_cache:
            cached = await cls._get_cached_script(cache_key)
            if cached:
                print(f"Using cached script: {cache_key}")
                return cached
        
        name = astrology_result.get('name', 'Friend')
        sun_sign = astrology_result.get('sun_sign', '')
        ascendant = astrology_result.get('ascendant', '')
        
        system_prompt = """You are an elite Arabic astrology consultant with deep knowledge of psychological analysis. 
Your style is warm, professional, evidence-based, and deeply empathetic. You combine ancient astrological wisdom 
with modern psychological insights. Speak directly to the person, making them feel seen, understood, and empowered."""
        
        user_prompt = f"""
Create a personalized 2-3 minute video script in Modern Standard Arabic for this astrological reading.

**Client Profile:**
Name: {name}
Sun Sign: {sun_sign}
Ascendant: {ascendant}
Birth Date: {astrology_result.get('birth_date', '')}
Day Type: {astrology_result.get('day_type', 'today')}

**Current Analysis:**
Psychological State: {astrology_result.get('psychological_state', '')}
Emotional State: {astrology_result.get('emotional_state', '')}
Mental Clarity: {astrology_result.get('mental_state', '')}
Physical Energy: {astrology_result.get('physical_state', '')}
Luck Level: {astrology_result.get('luck_level', '')}
Lucky Color: {astrology_result.get('lucky_color', '')}
Lucky Number: {astrology_result.get('lucky_number', '')}
Compatibility: {astrology_result.get('compatibility', '')}
Guidance: {astrology_result.get('advice', '')}
Cautions: {astrology_result.get('warning', '')}

**Script Structure:**
1. Warm Opening (15s)
   - Personal greeting using name
   - Create immediate connection
   
2. Astrological Foundation (30s)
   - Explain their sun sign essence
   - Ascendant influence on personality
   - Current planetary alignments
   
3. Deep Analysis (60s)
   - Psychological insights with empathy
   - Emotional patterns and needs
   - Mental clarity and focus areas
   - Physical energy management
   
4. Practical Guidance (30s)
   - Specific actionable advice
   - Lucky elements and how to use them
   - Relationship compatibility insights
   
5. Empowering Close (15s)
   - Affirming message
   - Future-focused encouragement
   - Memorable closing line

**Tone Guidelines:**
- Speak as a wise friend, not a fortune teller
- Use "أنت" (you) to create intimacy
- Balance validation with gentle challenge
- Include 2-3 specific examples or metaphors
- End on hope and agency

**Language:**
- Modern Standard Arabic (فصحى مبسطة)
- Avoid overly formal or classical terms
- Use short, impactful sentences
- Natural conversational flow
- No bullet points or lists in final script

Write only the spoken script, ready for voiceover.
"""
        
        try:
            response = await cls._get_openai_client().chat.completions.create(
                model=cls.MODELS.get(model, cls.MODELS["gpt4o"]),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                presence_penalty=0.3,
                frequency_penalty=0.3
            )
            
            script = response.choices[0].message.content.strip()
            
            if use_cache:
                await cls._cache_script(cache_key, script)
            
            return script
            
        except Exception as e:
            print(f"Script generation failed: {str(e)}")
            return cls._get_fallback_script(astrology_result)
    
    @classmethod
    def _get_fallback_script(cls, result: Dict[str, Any]) -> str:
        name = result.get('name', '')
        sun_sign = result.get('sun_sign', '')
        ascendant = result.get('ascendant', '')
        
        script = f"""
السلام عليكم {name}، أهلاً وسهلاً بك في تحليلك الفلكي الشخصي.

أنت من مواليد برج {sun_sign}، {f'وطالعك {ascendant}' if ascendant else ''}.

{result.get('psychological_state', '')}

{result.get('emotional_state', '')}

{result.get('mental_state', '')}

أما بالنسبة لطاقتك الجسدية، {result.get('physical_state', '')}.

حظك اليوم {result.get('luck_level', 'متوسط')}.

نصيحتي لك: {result.get('advice', '')}

{result.get('warning', '')}

تذكر دائماً أن الأبراج مجرد دليل، وأنت من يصنع مستقبلك بإرادتك وجهدك. كن قوياً ومتفائلاً!
        """
        
        return script.strip()
    
    @classmethod
    async def generate_psychology_script(
        cls,
        psychology_data: Dict[str, Any],
        model: str = "gpt4o",
        temperature: float = 0.85
    ) -> str:
        
        name = psychology_data.get('name', 'Friend')
        score = psychology_data.get('score', 0)
        level = psychology_data.get('level', '')
        message = psychology_data.get('message', '')
        supportive_messages = psychology_data.get('supportive_messages', [])
        
        system_prompt = """You are a compassionate Arabic psychological counselor with deep expertise in mental health. 
Your style is warm, non-judgmental, empathetic, and empowering. You help people understand their psychological state 
with kindness while providing practical, actionable guidance."""
        
        user_prompt = f"""
Create a compassionate 2-3 minute video script in Modern Standard Arabic for this psychological assessment.

**Client:**
Name: {name}
Assessment Score: {score}/21
Level: {level}
Main Message: {message}

**Supportive Messages:**
{chr(10).join(f'- {msg}' for msg in supportive_messages) if supportive_messages else 'None'}

**Requirements:**
1. Start with warm, personal greeting using name
2. Gently explain the assessment results without alarm
3. Validate their feelings and experiences  
4. Deliver the supportive messages naturally in your own words
5. Provide 2-3 practical coping strategies
6. End with hope, encouragement, and affirmation of their worth

**Style:**
- Warm, gentle, and deeply empathetic
- Use "you" (أنت) directly - personal and intimate
- Simple, clear Modern Standard Arabic
- No medical jargon or complex terms
- Focus on strength, resilience, and self-compassion
- Validate emotions while instilling hope
- Speak as a caring friend, not a distant expert

**Tone:**
- If score is low (7-10): Affirming and encouraging
- If score is moderate (11-14): Supportive and normalizing  
- If score is higher (15-21): Deeply compassionate and gently directive

Write ONLY the script in Arabic. No titles, headers, or formatting. Just warm, flowing speech.
"""
        
        try:
            model_name = cls.MODEL_MAPPING.get(model, "gpt-4o")
            
            response = await cls._get_openai_client().chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=temperature
            )
            
            script = response.choices[0].message.content.strip()
            return script
            
        except Exception as e:
            print(f"Psychology script generation failed: {str(e)}")
            return cls._get_fallback_psychology_script(psychology_data)
    
    @classmethod
    def _get_fallback_psychology_script(cls, data: Dict[str, Any]) -> str:
        name = data.get('name', '')
        level = data.get('level', '')
        message = data.get('message', '')
        supportive_messages = data.get('supportive_messages', [])
        
        script = f"""
السلام عليكم {name}، أهلاً وسهلاً بك.

شكراً لثقتك في مشاركة مشاعرك معنا.

{message}

{chr(10).join(supportive_messages)}

تذكر دائماً أن طلب الدعم هو علامة على القوة، وليس الضعف. أنت تستحق أن تشعر بالراحة والسلام.
        """
        
        return script.strip()
    
    @classmethod
    async def generate_comprehensive_script(
        cls,
        comprehensive_data: Dict[str, Any],
        model: str = "gpt4o",
        temperature: float = 0.85
    ) -> str:
        
        name = comprehensive_data.get('name', 'Friend')
        psych = comprehensive_data.get('psychology', {})
        neuro = comprehensive_data.get('neuroscience', {})
        astro = comprehensive_data.get('astrology', {})
        
        system_prompt = """You are an elite holistic wellness consultant who integrates psychology, neuroscience, and astrology. 
Your expertise spans mental health counseling, nervous system regulation, and astrological wisdom. You create deeply personalized, 
compassionate analyses that weave all three perspectives into a coherent, empowering narrative. Your style is warm, professional, 
insightful, and actionable."""
        
        user_prompt = f"""
Create a comprehensive 5-7 minute personalized video script in Modern Standard Arabic that integrates all three assessments.

**Client Profile:**
Name: {name}

**Psychological Assessment:**
- Score: {psych.get('score', 0)}/21
- Level: {psych.get('level', '')}
- Main Message: {psych.get('message', '')}
- Supportive Messages: {', '.join(psych.get('supportive_messages', []))}

**Nervous System Pattern:**
- Dominant: {neuro.get('dominant', '')}
- Secondary: {neuro.get('secondary', '')}
- Description: {neuro.get('description', '')}
- Scores: {neuro.get('scores', {})}

**Astrological Profile:**
- Sun Sign: {astro.get('sun_sign', '')}
- Ascendant: {astro.get('ascendant', '')}
- Psychological State: {astro.get('psychological_state', '')}
- Emotional State: {astro.get('emotional_state', '')}
- Mental State: {astro.get('mental_state', '')}
- Physical State: {astro.get('physical_state', '')}
- Luck: {astro.get('luck_level', '')}
- Lucky Color: {astro.get('lucky_color', '')}
- Lucky Number: {astro.get('lucky_number', '')}
- Compatibility: {astro.get('compatibility', '')}
- Advice: {astro.get('advice', '')}
- Warning: {astro.get('warning', '')}

**Structure (seamless flow, no headers):**

1. **Warm Opening** (30 seconds)
   - Greet {name} personally
   - Express excitement about this deep dive
   - Set tone: you're about to discover yourself at multiple levels

2. **Psychological Landscape** (90 seconds)
   - Gently introduce their psychological state
   - Contextualize the score without alarm
   - Weave in supportive messages naturally
   - Validate emotions, normalize experience
   - Connect it to their inner world

3. **Nervous System Wisdom** (90 seconds)
   - Explain their {neuro.get('dominant', '')} pattern simply
   - How it shows up in daily life
   - Why it makes sense given their psychology
   - Practical regulation techniques
   - Reframe it as adaptive, not broken

4. **Astrological Context** (120 seconds)
   - Introduce their celestial blueprint ({astro.get('sun_sign', '')})
   - How cosmic energies align with nervous system
   - Current planetary influences on mood
   - Lucky elements and timing
   - Practical spiritual guidance

5. **Integrated Synthesis** (60 seconds)
   - Weave all three together coherently
   - Show how psychology, neuroscience, and astrology tell one story
   - Actionable steps based on all three
   - Specific practices for THIS person

6. **Empowering Close** (30 seconds)
   - Deep affirmation of their worth
   - Hope and encouragement
   - Remind them they're not alone
   - End with warmth and love

**Critical Requirements:**
- Write as ONE FLOWING MONOLOGUE - no breaks, no headers, no section titles
- Use "you" (أنت) - direct, personal, intimate
- Transitions between topics must be seamless and natural
- Simple, beautiful Modern Standard Arabic
- No jargon - explain everything clearly
- Balance depth with accessibility
- Warm, compassionate, empowering tone throughout
- Practical and actionable, not just theoretical
- Make them feel SEEN, UNDERSTOOD, and HOPEFUL

**Tone Calibration:**
- If psychological score is concerning: Extra gentle, deeply validating, emphasize strength
- If nervous system is dysregulated: Normalize it, reframe as protective, offer hope
- If astrology suggests challenges: Frame as opportunities for growth

Write ONLY the script. No titles, no formatting. Just flowing, heartfelt Arabic speech that transforms lives.
"""
        
        try:
            model_name = cls.MODEL_MAPPING.get(model, "gpt-4o")
            
            response = await cls._get_openai_client().chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=3500,
                temperature=temperature
            )
            
            script = response.choices[0].message.content.strip()
            return script
            
        except Exception as e:
            print(f"Comprehensive script generation failed: {str(e)}")
            return cls._get_fallback_comprehensive_script(comprehensive_data)
    
    @classmethod
    def _get_fallback_comprehensive_script(cls, data: Dict[str, Any]) -> str:
        name = data.get('name', '')
        psych = data.get('psychology', {})
        neuro = data.get('neuroscience', {})
        astro = data.get('astrology', {})
        
        script = f"""
السلام عليكم {name}، أهلاً بك في رحلة اكتشاف الذات المتكاملة.

من الناحية النفسية، {psych.get('message', '')}

{chr(10).join(psych.get('supportive_messages', []))}

أما نظامك العصبي، فهو يعمل بنمط {neuro.get('dominant', '')}. {neuro.get('description', '')}

من الناحية الفلكية، أنت من برج {astro.get('sun_sign', '')}. {astro.get('psychological_state', '')}

{astro.get('advice', '')}

تذكر أن كل جوانب شخصيتك تعمل معاً لتجعلك الشخص الفريد الذي أنت عليه. أنت أقوى مما تعتقد.
        """
        
        return script.strip()
    
    @classmethod
    async def generate_voice(
        cls, 
        script: str, 
        output_path: str,
        voice: str = "nova",
        speed: float = 0.95,
        provider: Literal["openai", "elevenlabs"] = "openai"
    ) -> str:
        
        if provider == "elevenlabs" and cls._get_elevenlabs_key():
            return await cls._generate_voice_elevenlabs(script, output_path, voice, speed)
        
        return await cls._generate_voice_openai(script, output_path, voice, speed)
    
    @classmethod
    async def _generate_voice_openai(
        cls,
        script: str,
        output_path: str,
        voice: str,
        speed: float
    ) -> str:
        
        try:
            response = await cls._get_openai_client().audio.speech.create(
                model="tts-1-hd",
                voice=voice if voice in cls.VOICES else "nova",
                input=script,
                speed=speed
            )
            
            audio_path = Path(output_path) / f"audio_{voice}.mp3"
            audio_path.parent.mkdir(parents=True, exist_ok=True)
            
            response.stream_to_file(str(audio_path))
            
            print(f"OpenAI audio generated: {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            print(f"OpenAI voice generation failed: {str(e)}")
            raise
    
    @classmethod
    async def _generate_voice_elevenlabs(
        cls,
        script: str,
        output_path: str,
        voice: str,
        speed: float
    ) -> str:
        
        url = "https://api.elevenlabs.io/v1/text-to-speech/YOUR_VOICE_ID"
        
        headers = {
            "xi-api-key": cls._get_elevenlabs_key(),
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": script,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                audio_path = Path(output_path) / f"audio_elevenlabs.mp3"
                audio_path.parent.mkdir(parents=True, exist_ok=True)
                
                audio_path.write_bytes(response.content)
                
                print(f"ElevenLabs audio generated: {audio_path}")
                return str(audio_path)
                
        except Exception as e:
            print(f"ElevenLabs voice generation failed: {str(e)}")
            raise
    
    @classmethod
    async def generate_video_with_did(
        cls,
        script: str,
        voice: str = "nova",
        avatar: str = "arabic_female"
    ) -> str:
        """Generate a talking-head video with D-ID using text script directly.
        
        Uses D-ID's built-in Microsoft Azure TTS (Arabic voices) so no external
        audio URL is required — the local OpenAI MP3 cannot be passed to D-ID.
        """
        did_key = cls._get_did_key()
        if not did_key:
            raise Exception("D-ID API Key not found")
        
        url = "https://api.d-id.com/talks"
        
        headers = {
            "Authorization": f"Basic {did_key}",
            "Content-Type": "application/json"
        }
        
        avatar_url = cls.AVATAR_PRESETS.get(avatar, cls.AVATAR_PRESETS["arabic_female"])
        did_voice_id = cls.DID_VOICE_MAPPING.get(voice, "ar-SA-ZariyahNeural")
        
        payload = {
            "script": {
                "type": "text",
                "input": script,
                "provider": {
                    "type": "microsoft",
                    "voice_id": did_voice_id
                }
            },
            "source_url": avatar_url,
            "config": {
                "fluent": True,
                "pad_audio": 0.5,
                "result_format": "mp4"
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code not in (200, 201):
                    raise Exception(f"D-ID API error {response.status_code}: {response.text}")
                
                result = response.json()
                video_id = result.get("id")
                print(f"D-ID talk created: {video_id}")
                
                video_url = await cls._wait_for_video_completion(video_id)
                return video_url
                
        except Exception as e:
            print(f"D-ID video generation failed: {str(e)}")
            raise
    
    @classmethod
    async def _wait_for_video_completion(cls, video_id: str, max_wait: int = 300) -> str:
        
        url = f"https://api.d-id.com/talks/{video_id}"
        headers = {"Authorization": f"Basic {cls._get_did_key()}"}
        
        start_time = asyncio.get_event_loop().time()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                response = await client.get(url, headers=headers)
                result = response.json()
                
                status = result.get("status")
                print(f"D-ID status: {status}")
                
                if status == "done":
                    video_url = result.get("result_url")
                    print(f"Video ready: {video_url}")
                    return video_url
                
                elif status == "error":
                    error_msg = result.get("error", {}).get("description", "Unknown error")
                    raise Exception(f"D-ID video generation failed: {error_msg}")
                
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > max_wait:
                    raise Exception(f"Timeout waiting for D-ID video after {max_wait}s")
                
                await asyncio.sleep(5)
    
    @classmethod
    async def _download_video(cls, video_url: str, save_path: str) -> str:
        """Download the video from D-ID's temporary URL and save it locally."""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.get(video_url)
                response.raise_for_status()
                
                video_path = Path(save_path)
                video_path.parent.mkdir(parents=True, exist_ok=True)
                video_path.write_bytes(response.content)
                
                print(f"Video downloaded locally: {video_path} ({len(response.content) // 1024} KB)")
                return str(video_path)
        except Exception as e:
            print(f"Video download failed: {e}")
            return video_url  # Return original URL as fallback
    
    @classmethod
    async def _analyze_script_segments(cls, script: str) -> list:
        """Use GPT-4 to break the narration into emotional segments with visual prompts."""
        
        system_prompt = """You are a cinematic director. Analyze the following Arabic narration and break it into 3-4 emotional segments.

For each segment, provide:
1. "emotion": the dominant emotion (e.g. calm, hopeful, intense, reflective, warning, empowering)
2. "visual_prompt": a detailed Sora video prompt in English — describe a symbolic, immersive cinematic scene (NO talking heads, NO people looking at camera). Focus on nature, abstract visuals, cosmic imagery, symbolic metaphors. Include lighting, camera movement, and mood.
3. "duration": how many seconds this segment should be ("4", "8", or "12")

IMPORTANT RULES for visual_prompt:
- NO people talking to camera
- Use symbolic imagery: sunrise for hope, storm for struggle, calm ocean for peace, stars/cosmos for astrology, etc.
- Include camera movement: slow dolly, aerial, tracking shot, etc.
- Include lighting: golden hour, moonlight, dramatic shadows, soft glow, etc.
- Each scene must be visually DIFFERENT from the others
- Keep prompts under 200 words

Respond in valid JSON array format only, like:
[
  {"emotion": "calm", "visual_prompt": "...", "duration": "8"},
  {"emotion": "intense", "visual_prompt": "...", "duration": "12"},
  {"emotion": "hopeful", "visual_prompt": "...", "duration": "8"}
]"""

        try:
            client = cls._get_openai_client()
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Arabic narration to analyze:\n\n{script}"}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            raw = response.choices[0].message.content.strip()
            # Extract JSON from response
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            
            segments = json.loads(raw)
            print(f"📊 Script analyzed into {len(segments)} emotional segments")
            for i, seg in enumerate(segments):
                print(f"   Scene {i+1}: {seg['emotion']} ({seg['duration']}s)")
            return segments
            
        except Exception as e:
            print(f"⚠️ Script analysis failed: {e}, using default segments")
            return [
                {
                    "emotion": "reflective",
                    "visual_prompt": "Cinematic slow aerial shot over a calm desert at golden hour, sand dunes stretching to the horizon, warm golden light casting long shadows, gentle wind carrying sand particles that sparkle in the sunlight, shallow depth of field, peaceful and meditative atmosphere",
                    "duration": "12"
                },
                {
                    "emotion": "cosmic",
                    "visual_prompt": "Deep space visualization with swirling galaxies and nebulae in rich purple and gold colors, stars slowly rotating, cosmic dust clouds forming abstract patterns, camera slowly pushing through a field of stars, ethereal and mystical atmosphere, 4K cinematic quality",
                    "duration": "12"
                },
                {
                    "emotion": "hopeful",
                    "visual_prompt": "Breathtaking sunrise over a mountain range, golden rays piercing through clouds, morning mist in the valleys below, camera slowly rising upward revealing vast green landscape, warm colors transitioning from deep orange to bright gold, lens flares, cinematic drone shot, inspiring and uplifting mood",
                    "duration": "12"
                }
            ]
    
    @classmethod
    async def generate_video_with_sora(
        cls,
        script: str,
        output_path: str,
        audio_path: str = "",
        model: str = "sora-2-pro-2025-10-06",
        seconds: str = "12",
        size: str = "1280x720"
    ) -> str:
        """Generate a cinematic multi-scene video using Sora.
        
        Pipeline:
        1. GPT-4 analyzes narration into emotional segments
        2. Each segment → unique Sora cinematic scene (symbolic, no talking heads)
        3. ffmpeg concatenates scenes with crossfade transitions
        4. Narration audio overlaid on final video
        """
        import subprocess
        import concurrent.futures
        
        cls._reload_env()
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise Exception("OpenAI API Key not found")
        
        output_file = Path(output_path)
        session_dir = output_file.parent
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # ═══════════════════════════════════════════
        # Step 1: Analyze narration into segments
        # ═══════════════════════════════════════════
        print("🧠 Step 1: Analyzing narration into emotional segments...")
        segments = await cls._analyze_script_segments(script)
        
        # ═══════════════════════════════════════════
        # Step 2: Generate Sora clips for each segment
        # ═══════════════════════════════════════════
        print(f"🎥 Step 2: Generating {len(segments)} Sora scenes...")
        clip_paths = []
        
        def _generate_clip(idx, segment):
            """Generate a single Sora clip."""
            clip_path = str(session_dir / f"scene_{idx:02d}.mp4")
            client = OpenAI(api_key=api_key)
            
            print(f"   🎬 Scene {idx+1}/{len(segments)}: {segment['emotion']} ({segment['duration']}s)...")
            
            video = client.videos.create_and_poll(
                model=model,
                prompt=segment["visual_prompt"],
                size=size,
                seconds=segment.get("duration", "8")
            )
            
            if video.status != "completed":
                raise Exception(f"Scene {idx+1} failed: {video.status}")
            
            content = client.videos.download_content(video.id)
            with open(clip_path, "wb") as f:
                for chunk in content.iter_bytes():
                    f.write(chunk)
            
            try:
                client.videos.delete(video.id)
            except Exception:
                pass
            
            clip_kb = Path(clip_path).stat().st_size // 1024
            print(f"   ✅ Scene {idx+1} ready ({clip_kb} KB)")
            return clip_path
        
        loop = asyncio.get_event_loop()
        
        # Generate clips sequentially (Sora allows 1 concurrent)
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            for idx, segment in enumerate(segments):
                try:
                    clip_path = await loop.run_in_executor(
                        pool, _generate_clip, idx, segment
                    )
                    clip_paths.append(clip_path)
                except Exception as e:
                    error_msg = str(e)
                    print(f"   ❌ Scene {idx+1} failed: {error_msg}")
                    # If billing limit hit, stop trying more scenes
                    if "billing" in error_msg.lower() or "limit" in error_msg.lower():
                        print(f"   ⚠️ Billing limit reached. Using {len(clip_paths)} scene(s).")
                        break
        
        if not clip_paths:
            raise Exception("No scenes were generated. Check your OpenAI billing limit.")
        
        # ═══════════════════════════════════════════
        # Step 3: Assemble with ffmpeg
        # ═══════════════════════════════════════════
        print("🎬 Step 3: Assembling cinematic video...")
        
        if len(clip_paths) == 1:
            # Single clip — just use it
            assembled_path = clip_paths[0]
        else:
            assembled_path = str(session_dir / "assembled.mp4")
            
            # Re-encode all clips to same format for safe concat
            normalized = []
            for i, cp in enumerate(clip_paths):
                norm_path = str(session_dir / f"norm_{i:02d}.mp4")
                subprocess.run([
                    "ffmpeg", "-y", "-i", cp,
                    "-c:v", "libx264", "-preset", "fast",
                    "-crf", "23", "-r", "24",
                    "-vf", f"scale={size.replace('x', ':')},setsar=1",
                    "-an", norm_path
                ], capture_output=True, check=True)
                normalized.append(norm_path)
            
            # Concat all clips using demuxer
            concat_file = str(session_dir / "concat.txt")
            with open(concat_file, "w") as f:
                for norm in normalized:
                    f.write(f"file '{norm}'\n")
            
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_file,
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                assembled_path
            ], capture_output=True, check=True)
            
            print(f"   ✅ {len(normalized)} scenes assembled")
            
            # Cleanup
            for norm in normalized:
                Path(norm).unlink(missing_ok=True)
            Path(concat_file).unlink(missing_ok=True)
        
        # ═══════════════════════════════════════════
        # Step 4: Handle audio overlay
        # ═══════════════════════════════════════════
        if audio_path and Path(audio_path).exists():
            print("🔊 Step 4: Overlaying narration audio...")
            
            # Get audio duration
            probe_cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_path
            ]
            duration_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            audio_duration = float(duration_result.stdout.strip())
            
            # Get video duration
            probe_vid = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                assembled_path
            ]
            vid_result = subprocess.run(probe_vid, capture_output=True, text=True)
            video_duration = float(vid_result.stdout.strip())
            
            print(f"   Audio: {audio_duration:.1f}s | Video: {video_duration:.1f}s")
            
            # If video is shorter than audio, loop the assembled video
            if video_duration < audio_duration:
                looped_path = str(session_dir / "looped.mp4")
                subprocess.run([
                    "ffmpeg", "-y",
                    "-stream_loop", "-1",
                    "-i", assembled_path,
                    "-t", str(audio_duration),
                    "-c", "copy",
                    looped_path
                ], capture_output=True, check=True)
                
                # Clean assembled, use looped
                if assembled_path != clip_paths[0]:
                    Path(assembled_path).unlink(missing_ok=True)
                assembled_path = looped_path
            
            # Merge narration audio with video
            subprocess.run([
                "ffmpeg", "-y",
                "-i", assembled_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                str(output_file)
            ], capture_output=True, check=True)
            
            # Cleanup
            if assembled_path != clip_paths[0]:
                Path(assembled_path).unlink(missing_ok=True)
        else:
            # No audio — just rename assembled to output
            import shutil
            if assembled_path != str(output_file):
                shutil.move(assembled_path, str(output_file))
        
        # Cleanup scene files
        for cp in clip_paths:
            Path(cp).unlink(missing_ok=True)
        
        final_size = output_file.stat().st_size // 1024
        print(f"✅ Cinematic video ready: {output_file} ({final_size} KB)")
        return str(output_file)

    # ════════════════════════════════════════════════════════════════════
    # Stability AI Ultra  –  Image Generation → Cinematic Video
    # ════════════════════════════════════════════════════════════════════
    STABILITY_BASE_URL = "https://api.stability.ai"

    @classmethod
    async def _generate_stability_image(
        cls,
        prompt: str,
        output_path: str,
        negative_prompt: str = "",
        aspect_ratio: str = "16:9",
        output_format: str = "png",
    ) -> str:
        """Generate a single image with Stability AI Ultra."""
        api_key = cls._get_stability_key()
        if not api_key:
            raise Exception("STABILITY_API_KEY not found in .env")

        url = f"{cls.STABILITY_BASE_URL}/v2beta/stable-image/generate/ultra"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "image/*",
        }

        # Build multipart form fields (httpx requires `files=` for multipart)
        form_fields = {
            "prompt": (None, prompt[:10000]),
            "output_format": (None, output_format),
            "aspect_ratio": (None, aspect_ratio),
        }
        if negative_prompt:
            form_fields["negative_prompt"] = (None, negative_prompt)

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, headers=headers, files=form_fields)
            if resp.status_code >= 400:
                print(f"   ⚠️ Stability API error {resp.status_code}: {resp.text[:300]}")
            resp.raise_for_status()

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).write_bytes(resp.content)
            img_kb = len(resp.content) // 1024
            print(f"   ✅ Image saved: {output_path} ({img_kb} KB)")
            return output_path

    @classmethod
    async def generate_video_with_stability(
        cls,
        script: str,
        output_path: str,
        audio_path: str = "",
        aspect_ratio: str = "16:9",
        seconds_per_image: float = 8.0,
    ) -> str:
        """Generate a cinematic video using Stability AI Ultra images.

        Pipeline:
        1. GPT-4 analyses narration → emotional segments with visual prompts
        2. Stability AI Ultra generates a stunning image per segment
        3. ffmpeg creates video from images with Ken Burns zoom/pan effects
           and crossfade transitions
        4. Narration audio overlaid on final video
        """
        import subprocess

        stability_key = cls._get_stability_key()
        if not stability_key:
            raise Exception("STABILITY_API_KEY not found in .env")

        output_file = Path(output_path)
        session_dir = output_file.parent
        session_dir.mkdir(parents=True, exist_ok=True)

        # ──── Step 1: Analyse narration into segments ────
        print("🧠 [Stability] Step 1: Analysing narration into emotional segments…")
        segments = await cls._analyze_script_segments(script)

        # ──── Step 2: Generate images per segment ────
        print(f"🎨 [Stability] Step 2: Generating {len(segments)} cinematic image(s)…")
        image_paths: list[str] = []

        for idx, segment in enumerate(segments):
            prompt = segment["visual_prompt"]
            emotion = segment.get("emotion", "cinematic")
            img_path = str(session_dir / f"stability_scene_{idx:02d}.png")

            print(
                f"   🖼️ Image {idx + 1}/{len(segments)}: "
                f"{emotion}…"
            )

            try:
                await cls._generate_stability_image(
                    prompt=prompt,
                    output_path=img_path,
                    negative_prompt="blurry, low quality, text, watermark, logo, ugly, distorted",
                    aspect_ratio=aspect_ratio,
                )
                image_paths.append(img_path)
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ Image {idx + 1} failed: {error_msg}")
                if "billing" in error_msg.lower() or "credit" in error_msg.lower():
                    print("   ⚠️ Credit issue. Using available images.")
                    break

        if not image_paths:
            raise Exception(
                "No Stability AI images generated. Check STABILITY_API_KEY and credits."
            )

        # ──── Step 3: Create video from images with Ken Burns effect ────
        print(f"🎬 [Stability] Step 3: Creating cinematic video from {len(image_paths)} image(s)…")

        # Determine resolution from aspect ratio
        ar_map = {
            "16:9": (1920, 1080),
            "9:16": (1080, 1920),
            "1:1":  (1080, 1080),
            "4:3":  (1440, 1080),
            "3:4":  (1080, 1440),
            "21:9": (2560, 1080),
        }
        width, height = ar_map.get(aspect_ratio, (1920, 1080))

        # Ken Burns effects: alternate between zoom-in and pan
        ken_burns_effects = [
            # Slow zoom in from center
            f"scale=8000:-1,zoompan=z='min(zoom+0.0015,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(seconds_per_image*25)}:s={width}x{height}:fps=25",
            # Pan left to right
            f"scale=8000:-1,zoompan=z='1.3':x='if(lte(on,1),0,x+2)':y='ih/2-(ih/zoom/2)':d={int(seconds_per_image*25)}:s={width}x{height}:fps=25",
            # Slow zoom out
            f"scale=8000:-1,zoompan=z='if(lte(zoom,1.0),1.5,zoom-0.0015)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(seconds_per_image*25)}:s={width}x{height}:fps=25",
            # Pan right to left
            f"scale=8000:-1,zoompan=z='1.3':x='if(lte(on,1),iw,x-2)':y='ih/2-(ih/zoom/2)':d={int(seconds_per_image*25)}:s={width}x{height}:fps=25",
        ]

        clip_paths: list[str] = []
        for i, img in enumerate(image_paths):
            clip_path = str(session_dir / f"stability_clip_{i:02d}.mp4")
            effect = ken_burns_effects[i % len(ken_burns_effects)]

            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-loop", "1", "-i", img,
                    "-vf", effect,
                    "-t", str(seconds_per_image),
                    "-c:v", "libx264", "-preset", "fast",
                    "-crf", "20", "-pix_fmt", "yuv420p",
                    "-an", clip_path,
                ],
                capture_output=True, check=True,
            )
            clip_paths.append(clip_path)
            print(f"   ✅ Clip {i + 1} ({seconds_per_image}s with Ken Burns effect)")

        # Concatenate clips with crossfade
        if len(clip_paths) == 1:
            assembled_path = clip_paths[0]
        else:
            assembled_path = str(session_dir / "stability_assembled.mp4")
            # Build complex crossfade filter
            crossfade_dur = 1.0  # 1 second crossfade
            inputs = []
            for cp in clip_paths:
                inputs.extend(["-i", cp])

            # Simple concat (crossfade can be complex, use safe concat)
            concat_file = str(session_dir / "stability_concat.txt")
            with open(concat_file, "w") as f:
                for cp in clip_paths:
                    f.write(f"file '{Path(cp).resolve()}'\n")

            subprocess.run(
                [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", concat_file,
                    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                    "-pix_fmt", "yuv420p",
                    assembled_path,
                ],
                capture_output=True, check=True,
            )
            Path(concat_file).unlink(missing_ok=True)
            print(f"   ✅ {len(clip_paths)} clips assembled")

        # ──── Step 4: Audio overlay ────
        if audio_path and Path(audio_path).exists():
            print("🔊 [Stability] Step 4: Overlaying narration audio…")

            def _probe_duration(p):
                result = subprocess.run(
                    [
                        "ffprobe", "-v", "error",
                        "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", p,
                    ],
                    capture_output=True, text=True,
                )
                return float(result.stdout.strip())

            audio_dur = _probe_duration(audio_path)
            video_dur = _probe_duration(assembled_path)
            print(f"   Audio: {audio_dur:.1f}s | Video: {video_dur:.1f}s")

            if video_dur < audio_dur:
                looped = str(session_dir / "stability_looped.mp4")
                subprocess.run(
                    [
                        "ffmpeg", "-y",
                        "-stream_loop", "-1",
                        "-i", assembled_path,
                        "-t", str(audio_dur),
                        "-c", "copy", looped,
                    ],
                    capture_output=True, check=True,
                )
                if assembled_path != clip_paths[0]:
                    Path(assembled_path).unlink(missing_ok=True)
                assembled_path = looped

            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", assembled_path,
                    "-i", audio_path,
                    "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k",
                    "-map", "0:v:0", "-map", "1:a:0",
                    "-shortest",
                    str(output_file),
                ],
                capture_output=True, check=True,
            )

            if assembled_path != clip_paths[0]:
                Path(assembled_path).unlink(missing_ok=True)
        else:
            import shutil
            if assembled_path != str(output_file):
                shutil.move(assembled_path, str(output_file))

        # Clean up
        for cp in clip_paths:
            Path(cp).unlink(missing_ok=True)
        for img in image_paths:
            pass  # Keep images for reference

        final_kb = output_file.stat().st_size // 1024
        print(f"✅ [Stability] Cinematic video ready: {output_file} ({final_kb} KB)")
        return str(output_file)
    
    @classmethod
    async def generate_video_simple(cls, script: str, output_dir: str) -> Dict[str, str]:
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        audio_path = await cls.generate_voice(script, str(output_path))
        
        return {
            "script": script,
            "audio_path": audio_path,
            "status": "completed"
        }
    
    @classmethod
    async def generate_full_video(
        cls, 
        astrology_result: Dict[str, Any], 
        output_dir: str = "videos",
        model: str = "gpt4o",
        voice: str = "nova",
        speed: float = 0.95,
        use_cache: bool = True,
        include_video: bool = False,
        avatar: str = "arabic_female"
    ) -> Dict[str, Any]:
        
        print("🎬 Starting AI video generation...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = Path(output_dir) / timestamp
        session_dir.mkdir(parents=True, exist_ok=True)
        
        data_type = astrology_result.get('type', 'astrology')
        
        metadata = {
            "timestamp": timestamp,
            "model": model,
            "voice": voice,
            "speed": speed,
            "data_type": data_type,
            "input_data": astrology_result
        }
        
        try:
            print(f"📝 Generating script with {model}...")
            
            if data_type == 'psychology':
                script = await cls.generate_psychology_script(
                    astrology_result,
                    model=model
                )
            elif data_type == 'comprehensive':
                script = await cls.generate_comprehensive_script(
                    astrology_result,
                    model=model
                )
            else:
                script = await cls.generate_script(
                    astrology_result,
                    model=model,
                    use_cache=use_cache
                )
            
            (session_dir / "script.txt").write_text(script, encoding='utf-8')
            
            print(f"🎤 Generating voice ({voice})...")
            audio_path = await cls.generate_voice(
                script,
                str(session_dir),
                voice=voice,
                speed=speed
            )
            
            video_url = None
            video_path = None
            if include_video:
                print("🎥 Generating video with Sora...")
                try:
                    video_path = await cls.generate_video_with_sora(
                        script=script,
                        output_path=str(session_dir / "video.mp4"),
                        audio_path=audio_path
                    )
                    video_url = video_path
                except Exception as e:
                    print(f"⚠️  Sora video generation failed: {e}")
                    # Fallback 1: Stability AI Ultra images → cinematic video
                    if cls._get_stability_key():
                        print("🔄 Trying Stability AI as fallback...")
                        try:
                            video_path = await cls.generate_video_with_stability(
                                script=script,
                                output_path=str(session_dir / "video.mp4"),
                                audio_path=audio_path
                            )
                            video_url = video_path
                        except Exception as e_stab:
                            print(f"⚠️  Stability AI fallback failed: {e_stab}")
                            # Fallback 2: D-ID
                            if cls._get_did_key():
                                print("🔄 Trying D-ID as fallback...")
                                try:
                                    did_url = await cls.generate_video_with_did(
                                        script=script,
                                        voice=voice,
                                        avatar=avatar
                                    )
                                    local_video_path = str(session_dir / "video.mp4")
                                    video_path = await cls._download_video(did_url, local_video_path)
                                    video_url = did_url
                                except Exception as e2:
                                    print(f"⚠️  D-ID fallback also failed: {e2}")
                    elif cls._get_did_key():
                        print("🔄 Trying D-ID as fallback...")
                        try:
                            did_url = await cls.generate_video_with_did(
                                script=script,
                                voice=voice,
                                avatar=avatar
                            )
                            local_video_path = str(session_dir / "video.mp4")
                            video_path = await cls._download_video(did_url, local_video_path)
                            video_url = did_url
                        except Exception as e2:
                            print(f"⚠️  D-ID fallback also failed: {e2}")
            
            metadata.update({
                "script": script,
                "script_length": len(script),
                "word_count": len(script.split()),
                "audio_path": audio_path,
                "video_path": video_path,
                "video_url": video_url,
                "session_dir": str(session_dir)
            })
            
            (session_dir / "metadata.json").write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            
            result = {
                "status": "success",
                "script": script,
                "audio_path": audio_path,
                "video_path": video_path,
                "video_url": video_url,
                "session_dir": str(session_dir),
                "metadata": metadata,
                "message": "Generation completed successfully"
            }
            
            print("✅ Video generation successful!")
            return result
            
        except Exception as e:
            print(f"❌ Video generation error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "session_dir": str(session_dir),
                "message": "Video generation failed"
            }
