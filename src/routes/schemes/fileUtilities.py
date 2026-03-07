from pydantic import BaseModel
from typing import List, Dict, Optional

class DuplicateFile(BaseModel):
    filename: str
    path: str
    size: int

class ScanDuplicatesResponse(BaseModel):
    signal: str
    directory: str
    file_type: str
    total_files_scanned: int
    duplicates_count: int
    duplicates: Dict[str, List[DuplicateFile]]


class LargeFile(BaseModel):
    filename: str
    path: str
    size: int
    size_mb: float

class LargeFilesResponse(BaseModel):
    signal: str
    directory: str
    total_files_scanned: int
    top_n: int
    files: List[LargeFile]

class FoundFile(BaseModel):
    filename: str
    path: str
    size_mb: float

class SearchFilesResponse(BaseModel):
    signal: str
    directory: str
    file_type: str
    filename_contains: Optional[str]
    total_found: int
    files: List[FoundFile]

class UnlockPDFResult(BaseModel):
    filename: str
    status: str        # "unlocked" | "password_required" | "error"
    message: str


class UnlockPDFResponse(BaseModel):
    signal: str
    input_folder: str
    output_folder: str
    total_found: int
    total_unlocked: int
    total_failed: int
    results: List[UnlockPDFResult]


class ConvertPDFResult(BaseModel):
    filename: str
    status: str        # "converted" | "error"
    message: str


class ConvertPDFResponse(BaseModel):
    signal: str
    input_folder: str
    output_folder: str
    dpi: int
    total_found: int
    total_converted: int
    total_failed: int
    results: List[ConvertPDFResult]