# Abrag — Mental Wellness & Astrology API

> A powerful FastAPI backend that combines **Psychology**, **Neuroscience**, **Astrology**, and **Letter Science** to deliver personalized AI-generated insights and videos.

---

## Features

- **Letter Science** — Analyze governing letters based on name & age
- **Psychology Assessment** — 7-question mental health evaluation
- **Neuroscience Assessment** — Nervous system pattern detection
- **Astrology Analysis** — Real-time planetary data via Free Astrology API
- **AI Video Generation** — GPT-4o script → TTS audio → Stability AI visuals → FFmpeg video
- **Comprehensive Analysis** — All four sciences combined in one request

---

## ️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Server | Uvicorn |
| AI / LLM | OpenAI GPT-4o |
| TTS | OpenAI TTS-1-HD |
| Image Gen | Stability AI Ultra |
| Video | FFmpeg |
| Astrology | Free Astrology API |
| Validation | Pydantic v2 |

---

## Getting Started

### Prerequisites

- Python 3.11+
- FFmpeg installed on the system
- API keys (see [Environment Variables](#-environment-variables))

### Installation

```bash
# Clone the repo
git clone https://github.com/your-org/abrag.git
cd abrag

# Create virtual environment
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> API will be live at `http://localhost:8000` 
> Swagger docs at `http://localhost:8000/docs`

---

## Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=sk-...
STABILITY_API_KEY=sk-...
D_ID_API_KEY=...
ELEVENLABS_API_KEY=... # optional
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info |
| `GET` | `/health` | Health check |
| `POST` | `/letter/analyze` | Letter science analysis |
| `GET` | `/letter/dictionary` | Full guidance dictionary |
| `POST` | `/astrology/analyze` | Daily horoscope analysis |
| `POST` | `/astrology/generate-video` | AI astrology video |
| `GET` | `/astrology/voices` | Available TTS voices |
| `GET` | `/astrology/models` | Available AI models |
| `GET` | `/psychology` | Get 7 psychology questions |
| `POST` | `/psychology/submit` | Submit answers & get result |
| `POST` | `/psychology/generate-video` | AI psychology video |
| `POST` | `/comprehensive/submit` | Full analysis (no video) |
| `POST` | `/comprehensive/generate-video` | Full analysis + AI video |

---

## Request & Response Examples

### Letter Science
```http
POST /letter/analyze
Content-Type: application/json

{
"name": "Ahmed Mohamed",
"age": 25
}
```
```json
{
"name": "Ahmed Mohamed",
"age": 25,
"letters_count": 12,
"stage": 2,
"governing_letter": "ح",
"guidance_type": "spiritual",
"guidance": "Focus on spiritual connection",
"is_dependent": false
}
```

---

### Comprehensive Analysis
```http
POST /comprehensive/submit
Content-Type: application/json

{
"name": "Ahmed",
"psychology_answers": [1, 2, 1, 3, 2, 1, 2],
"neuroscience_answers": ["A", "B", "A", "C", "D", "A", "B", "C", "A"],
"birth_date": "1990-05-15",
"birth_time": "14:30",
"birth_place": "Cairo",
"gender": "male",
"day_type": "today"
}
```
```json
{
"psychology": { "score": 12, "level": "...", "message": "..." },
"neuroscience": { "dominant": "Fight", "secondary": "Fawn", "description": "..." },
"astrology": { "sun_sign": "Taurus", "ascendant": "Sagittarius", "advice": "..." }
}
```

---

### AI Video Generation
```http
POST /comprehensive/generate-video?model=gpt4o&voice=nova
Content-Type: application/json

{
"name": "Ahmed",
"psychology_answers": [1, 2, 1, 3, 2, 1, 2],
"neuroscience_answers": ["A", "B", "A", "C", "D", "A", "B", "C", "A"],
"birth_date": "1990-05-15",
"day_type": "today"
}
```
```json
{
"analysis": { ... },
"video": {
"status": "success",
"audio_path": "videos/comprehensive/TIMESTAMP/audio_nova.mp3",
"video_path": "videos/comprehensive/TIMESTAMP/video.mp4"
}
}
```

> ⏱️ Video generation takes **5–15 minutes**. Plan your UX accordingly (show a loading screen).

---

## Video Generation Pipeline

```
User Data
│
▼
GPT-4o generates Arabic script
│
▼
OpenAI TTS converts script to audio (.mp3)
│
▼
GPT-4o segments script into emotional scenes
│
▼
Stability AI generates an image per scene
│
▼
FFmpeg applies Ken Burns effects + crossfades
│
▼
Final video (.mp4) with narration overlay
```

---

## Project Structure

```
abrag/
├── main.py # FastAPI app entry point
├── requirements.txt
├── .env # API keys (not committed)
├── app/
│ ├── models/ # Pydantic request/response models
│ │ ├── astrology.py
│ │ ├── comprehensive.py
│ │ ├── letter.py
│ │ ├── neuroscience.py
│ │ └── psychology.py
│ ├── routes/ # API route handlers
│ │ ├── astrology.py
│ │ ├── comprehensive.py
│ │ ├── letter.py
│ │ ├── neuroscience.py
│ │ └── psychology.py
│ └── services/ # Business logic
│ ├── ai_video_service.py
│ ├── astrology_service.py
│ ├── comprehensive_service.py
│ ├── letter_service.py
│ ├── neuroscience_service.py
│ ├── psychology_service.py
│ └── video_analytics.py
├── videos/ # Generated audio/video output
└── cache/ # Cached GPT scripts
```

---

## Available Voices

| Voice | Gender |
|-------|--------|
| `nova` | Female |
| `shimmer` | Female |
| `alloy` | Neutral |
| `fable` | Neutral |
| `echo` | Male |
| `onyx` | Male |

---

## Deployment

The project is configured for **Railway** deployment:

```toml
# railway.toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

```
# Procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## CORS

All origins are currently allowed for development:

```python
allow_origins=["*"]
```

> ️ Restrict this to your Flutter app's domain in production.

---

## License

MIT License — feel free to use and modify.

---

<div align="center">
<strong>Built with FastAPI · Powered by OpenAI · Deployed on Railway</strong>
</div>
