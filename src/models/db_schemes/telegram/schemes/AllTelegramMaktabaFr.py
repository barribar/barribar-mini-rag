from .telegram_base import TelegramSQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy.orm import relationship
from pydantic import BaseModel

class AllTelegramMaktabaFr(TelegramSQLAlchemyBase):

    __tablename__ = "all_telegram_maktaba_fr"

    maktaba_id  = Column(Integer, primary_key=True, autoincrement=True)
    maktaba_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    maktaba_name =  Column(String, nullable=False)
    maktaba_link = Column(String, nullable=False, unique=True)
    maktaba_info  = Column(String, nullable=True)
    maktaba_at  = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    
    # Relation vers AllTelegramKotobFr
    kotob_fr = relationship("AllTelegramKotobFr", back_populates="maktaba_fr")
    
    
