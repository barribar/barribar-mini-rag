from pydantic import BaseModel
from typing import List, Optional

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