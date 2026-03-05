from pydantic import BaseModel
from typing import List

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