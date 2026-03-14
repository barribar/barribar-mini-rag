from .telegram_base import TelegramSQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, Text,UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy.orm import relationship
from pydantic import BaseModel

class AllTelegramMaktabaFr(TelegramSQLAlchemyBase):

    __tablename__ = "all_telegram_maktaba_fr"

    maktaba_id = Column(Integer, primary_key=True, autoincrement=True)
    # maktaba_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    maktaba_name = Column(Text, nullable=False)
    maktaba_link = Column(Text, nullable=False)
    maktaba_info = Column(Text, nullable=True)
    maktaba_at = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    
    # Relation vers AllTelegramKotobFr
    kotob_fr = relationship("AllTelegramKotobFr", back_populates="maktaba_fr")
    
    __table_args__ = (
        UniqueConstraint("maktaba_link", name="all_telegram_maktaba_fr_link_key"),
    )
    