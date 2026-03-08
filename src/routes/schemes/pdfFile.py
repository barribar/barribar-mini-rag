from pydantic import BaseModel
from typing import List, Optional


class ScannedFile(BaseModel):
    filename: str
    path: str
    file_type: str
    size: int
    size_mb: float


class ScanPdfFilesResponse(BaseModel):
    signal: str
    directory: str
    total_found: int
    files: List[ScannedFile]


class InsertedFile(BaseModel):
    filename: str
    path: str
    status: str       # "inserted" | "skipped" | "error"
    message: str


class InsertPdfFilesResponse(BaseModel):
    signal: str
    total_scanned: int
    total_inserted: int
    total_skipped: int
    total_failed: int