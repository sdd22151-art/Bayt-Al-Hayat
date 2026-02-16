from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import psychology_router

# إنشاء تطبيق FastAPI
app = FastAPI(
    title="Psychology Assessment API",
    description="API لتقييم الحالة النفسية",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# إضافة CORS middleware للسماح بالطلبات من تطبيق الموبايل
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # في الإنتاج، استبدل * بالنطاقات المحددة
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تسجيل الـ routes
app.include_router(psychology_router)


@app.get("/")
async def root():
    """الصفحة الرئيسية للـ API"""
    return {
        "message": "مرحبًا بك في API تقييم الحالة النفسية",
        "version": "1.0.0",
        "endpoints": {
            "get_questions": "GET /psychology",
            "submit_answers": "POST /psychology/submit",
            "documentation": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """فحص صحة الخادم"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
