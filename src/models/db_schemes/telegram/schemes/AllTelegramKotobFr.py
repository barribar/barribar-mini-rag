from .telegram_base import TelegramSQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, BigInteger, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from sqlalchemy import Index

class AllTelegramKotobFr(TelegramSQLAlchemyBase):
    __tablename__ = "all_telegram_kotob_fr"

    maktaba       = Column(Integer, ForeignKey("all_telegram_maktaba_fr.maktaba_id", 
                           deferrable=True, 
                           initially="DEFERRED"), 
                           nullable=False)
    
    kitab_id     = Column(BigInteger, primary_key=True)
    # kitab_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    kitab_title  = Column(String, nullable=True)
    kitab_message= Column(String, nullable=True)
    kitab_date   = Column(String, nullable=True)
    kitab_size   = Column(BigInteger, nullable=True)
    kitab_link   = Column(String, nullable=True)
    kitab_group  = Column(String, nullable=True)



    __table_args__ = (
        # Clé primaire composite (maktaba, kitab_id)
        PrimaryKeyConstraint("maktaba", "kitab_id", name="all_telegram_kotob_fr_pkey"),
    )

    # Relation vers AllTelegramMaktabaFr
    maktaba_fr  = relationship("AllTelegramMaktabaFr", back_populates="kotob_fr")


