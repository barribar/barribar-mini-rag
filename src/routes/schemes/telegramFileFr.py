from pydantic import BaseModel
from typing import List, Optional


class InsertedTelegramFilesFr(BaseModel):
    filename: str
    path: str
    status: str       # "inserted" | "skipped" | "error"
    message: str


class InsertTelegramFilesResponseFr(BaseModel):
    signal: str
    total_scanned: int
    total_inserted: int
    total_skipped: int
    total_failed: int


class TelechargerTelegramResponseFr(BaseModel):
    signal: str
    maktaba_id: int
    channel: str
    total_inserted: int
    total_skipped: int
    total_failed: int