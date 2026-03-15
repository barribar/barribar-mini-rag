from pydantic import BaseModel
from typing import List, Optional


class InsertedTelegramFilesAr(BaseModel):
    filename: str
    path: str
    status: str       # "inserted" | "skipped" | "error"
    message: str


class InsertTelegramFilesResponseAr(BaseModel):
    signal: str
    total_scanned: int
    total_inserted: int
    total_skipped: int
    total_failed: int


class TelechargerTelegramResponseAr(BaseModel):
    signal: str
    maktaba_id: int
    channel: str
    total_inserted: int
    total_skipped: int
    total_failed: int