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