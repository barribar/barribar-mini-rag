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

from pydantic import BaseModel
from typing import List

# ---------------------------
# Pour /unlockPDF
# ---------------------------
class UnlockPDFResult(BaseModel):
    filename: str
    status: str
    message: str

class UnlockPDFResponse(BaseModel):
    signal: str
    input_folder: str
    output_folder: str
    total_found: int
    total_unlocked: int
    total_failed: int
    results: List[UnlockPDFResult]

# ---------------------------
# Pour /convertPdfToBwGhostscript
# ---------------------------
class ConvertPDFResult(BaseModel):
    filename: str
    status: str
    message: str

class ConvertPDFResponse(BaseModel):
    signal: str
    input_folder: str
    output_folder: str
    total_found: int
    total_converted: int
    total_failed: int
    results: List[ConvertPDFResult]