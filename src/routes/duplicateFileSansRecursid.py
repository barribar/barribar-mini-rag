from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from .schemes.duplicateFile import DuplicateFile, ScanDuplicatesResponse
import os
import hashlib
import logging

logger = logging.getLogger('uvicorn.error')

duplicate_router = APIRouter(
    prefix="/api/v1/duplicatesSansRecursif",
    tags=["api_v1", "duplicatesSansRecursif"],
)

@duplicate_router.post("/scanSansRecursif", response_model=ScanDuplicatesResponse)
async def scan_duplicates(request: Request, directory: str, file_type: str,
                          app_settings: Settings = Depends(get_settings)):

    if not os.path.exists(directory) or not os.path.isdir(directory):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": "INVALID_DIRECTORY"}
        )

    hash_map = {}
    total_files_scanned = 0

    # Scan uniquement le répertoire racine (non récursif)
    for filename in os.listdir(directory):
        if not filename.lower().endswith(f".{file_type.strip('.')}"):
            continue

        file_path = os.path.join(directory, filename)
        if not os.path.isfile(file_path):
            continue

        total_files_scanned += 1

        hasher = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                    hasher.update(chunk)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            continue

        file_hash = hasher.hexdigest()
        hash_map.setdefault(file_hash, []).append(
            DuplicateFile(
                filename=filename,
                path=file_path,
                size=os.path.getsize(file_path),
            )
        )

    duplicates = {
        hash_val: files
        for hash_val, files in hash_map.items()
        if len(files) > 1
    }

    return ScanDuplicatesResponse(
        signal="SCAN_SUCCESS",
        directory=directory,
        file_type=file_type,
        total_files_scanned=total_files_scanned,
        duplicates_count=sum(len(v) for v in duplicates.values()),
        duplicates=duplicates,
    )