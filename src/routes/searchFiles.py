from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from .schemes.searchFiles import FoundFile, SearchFilesResponse
from typing import Optional
import os
import logging

logger = logging.getLogger('uvicorn.error')

search_files_router = APIRouter(
    prefix="/api/v1/search-files",
    tags=["api_v1", "search-files"],
)

@search_files_router.post("/scan", response_model=SearchFilesResponse)
async def search_files(request: Request, directory: str, file_type: str = "*",
                       filename_contains: Optional[str] = None,
                       app_settings: Settings = Depends(get_settings)):

    if not os.path.exists(directory) or not os.path.isdir(directory):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": "INVALID_DIRECTORY"}
        )

    found_files = []
    extension = None if file_type == "*" else f".{file_type.strip('.')}"

    for root, dirs, files in os.walk(directory):
        for filename in files:

            # Filter by extension
            if extension and not filename.lower().endswith(extension):
                continue

            # Filter by name contains
            if filename_contains and filename_contains.lower() not in filename.lower():
                continue

            file_path = os.path.join(root, filename)
            try:
                size = os.path.getsize(file_path)
                found_files.append(
                    FoundFile(
                        filename=filename,
                        path=file_path,
                        size_mb=round(size / (1024 * 1024), 2)
                    )
                )
            except (FileNotFoundError, OSError):
                continue
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                continue

    return SearchFilesResponse(
        signal="SEARCH_SUCCESS",
        directory=directory,
        file_type=file_type,
        filename_contains=filename_contains,
        total_found=len(found_files),
        files=found_files,
    )
