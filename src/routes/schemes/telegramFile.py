from pydantic import BaseModel
from typing import List, Optional


class InsertedTelegramFiles(BaseModel):
    filename: str
    path: str
    status: str       # "inserted" | "skipped" | "error"
    message: str


class InsertTelegramFilesResponse(BaseModel):
    signal: str
    total_scanned: int
    total_inserted: int
    total_skipped: int
    total_failed: int
