from .pdf_file_base import PdfSQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy.orm import relationship
from pydantic import BaseModel

class pdfFileDatabase(PdfSQLAlchemyBase):

    __tablename__ = "pdfFile"
    
    pdfFile_id = Column(Integer, primary_key=True, autoincrement=True)
    pdfFile_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    pdfFile_name = Column(String, nullable=False)
    pdfFile_author = Column(String, nullable=True)
    pdfFile_type = Column(String, nullable=False)
    pdfFile_size = Column(Integer, nullable=False)
    pdfFile_path = Column(String, nullable=True)
    # pdfFile_config = Column(JSONB, nullable=True)
    
    # created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    

    #chunks = relationship("DataChunk", back_populates="project")
    #assets = relationship("Asset", back_populates="project")

class RetrievedPdfDocument(BaseModel):
    text: str
    score: float
