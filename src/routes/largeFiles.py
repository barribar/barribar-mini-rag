from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from .schemes.largeFiles import LargeFile, LargeFilesResponse
import os
import logging

logger = logging.getLogger('uvicorn.error')

large_files_router = APIRouter(
    prefix="/api/v1/large-files",
    tags=["api_v1", "large-files"],
)

@large_files_router.post("/scan", response_model=LargeFilesResponse)
async def scan_large_files(request: Request, directory: str, top_n: int = 10,
                           app_settings: Settings = Depends(get_settings)):

    if not os.path.exists(directory) or not os.path.isdir(directory):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": "INVALID_DIRECTORY"}
        )

    all_files = []
    total_files_scanned = 0

    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                size = os.path.getsize(file_path)
                total_files_scanned += 1
                all_files.append(
                    LargeFile(
                        filename=filename,
                        path=file_path,
                        size=size,
                        size_mb=round(size / (1024 * 1024), 2)
                    )
                )
            
            except (FileNotFoundError, OSError):
                continue

            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                continue

    # Sort by size descending and take top_n
    top_files = sorted(all_files, key=lambda x: x.size, reverse=True)[:top_n]

    return LargeFilesResponse(
        signal="SCAN_SUCCESS",
        directory=directory,
        total_files_scanned=total_files_scanned,
        top_n=top_n,
        files=top_files,
    )