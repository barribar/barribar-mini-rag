from .telegram_base import TelegramSQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from sqlalchemy import Index

class AllTelegramKotobFr(TelegramSQLAlchemyBase):
    __tablename__ = "all_telegram_kotob_fr"

    
    kitab_id     = Column(BigInteger, primary_key=True)
    kitab_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    kitab_title  = Column(String, nullable=True)
    kitab_message= Column(String, nullable=True)
    kitab_date   = Column(String, nullable=True)
    kitab_size   = Column(BigInteger, nullable=True)
    kitab_link   = Column(String, nullable=True)
    kitab_group  = Column(String, nullable=True)

    # ForeignKey
    maktaba      = Column(Integer, ForeignKey("all_telegram_maktaba_fr.maktaba_id"), primary_key=True)

    # Unicité composite kitab_id + kitab_link
    __table_args__ = (
        UniqueConstraint("kitab_id", "kitab_link", name="uq_kitab_id_link"),
    )

    # Relation vers AllTelegramMaktabaFr
    maktaba_fr  = relationship("AllTelegramMaktabaFr", back_populates="kotob_fr")


