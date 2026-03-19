from sqlalchemy import Column, String, Boolean, DateTime, Text
from datetime import datetime
from app.database import Base


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String, primary_key=True)          # e.g. "openai_api_key"
    value = Column(Text, nullable=True, default="")  # actual value
    group = Column(String, nullable=False)           # "ai_models" | "payment_gateway"
    label = Column(String, nullable=False)           # human-readable label
    description = Column(String, nullable=True)      # extra info
    is_secret = Column(Boolean, default=True)        # mask value in GET responses
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
