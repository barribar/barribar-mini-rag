from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from routes.schemes.pdfFile import (ScannedFile, ScanPdfFilesResponse,
                                    InsertedFile, InsertPdfFilesResponse)
from models.PdfFileModel import PdfFileModel
import os
import logging

logger = logging.getLogger('uvicorn.error')

pdfFile_router = APIRouter(
    prefix="/api/v1/pdfFile",
    tags=["api_v1", "pdfFile"],
)


@pdfFile_router.post("/scan", response_model=ScanPdfFilesResponse)
async def scan_files(request: Request, directory: str,
                     file_type: str = "*",
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
            if extension and not filename.lower().endswith(extension):
                continue

            file_path = os.path.join(root, filename)
            try:
                size = os.path.getsize(file_path)
                ext = os.path.splitext(filename)[1].lstrip(".").lower() or "unknown"
                found_files.append(
                    ScannedFile(
                        filename=filename,
                        path=file_path,
                        file_type=ext,
                        size=size,
                        size_mb=round(size / (1024 * 1024), 2)
                    )
                )
            except (FileNotFoundError, OSError):
                continue
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                continue

    return ScanPdfFilesResponse(
        signal="SCAN_SUCCESS",
        directory=directory,
        total_found=len(found_files),
        files=found_files,
    )


@pdfFile_router.post("/scan-and-insert", response_model=InsertPdfFilesResponse)
async def scan_and_insert(request: Request, directory: str,
                          file_type: str = "*",
                          app_settings: Settings = Depends(get_settings)):

    if not os.path.exists(directory) or not os.path.isdir(directory):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": "INVALID_DIRECTORY"}
        )

    pdf_model = await PdfFileModel.create_instance(
        db_client=request.app.pdf_db_client
    )

    total_scanned = 0
    total_inserted = 0
    total_skipped = 0
    total_failed = 0

    extension = None if file_type == "*" else f".{file_type.strip('.')}"

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if extension and not filename.lower().endswith(extension):
                continue

            file_path = os.path.join(root, filename)
            try:
                size = os.path.getsize(file_path)
                ext = os.path.splitext(filename)[1].lstrip(".").lower() or "unknown"
                total_scanned += 1

                # Check duplicate par path complet
                existing = await pdf_model.get_by_path(file_path)
                if existing:
                    total_skipped += 1
                    continue

                await pdf_model.insert_one(
                    filename=filename,
                    path=file_path,
                    file_type=ext,
                    size=size,
                )
                total_inserted += 1
                logger.info(f"[{total_inserted}/{total_scanned}] Inséré : {filename}")

            except (FileNotFoundError, OSError):
                continue
            except Exception as e:
                logger.error(f"Erreur sur {file_path}: {e}")
                total_failed += 1

    return InsertPdfFilesResponse(
        signal="INSERT_SUCCESS",
        total_scanned=total_scanned,
        total_inserted=total_inserted,
        total_skipped=total_skipped,
        total_failed=total_failed,
    )