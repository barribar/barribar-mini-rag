from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from routes.schemes.fileUtilities  import (ScanDuplicatesResponse, DuplicateFile, 
                            LargeFile, LargeFilesResponse,
                            FoundFile, SearchFilesResponse)
from typing import Optional
import os
import hashlib
import logging


from pdf2image import convert_from_path
from PIL import Image




logger = logging.getLogger('uvicorn.error')

fileUtilities_router = APIRouter(
    prefix="/api/v1/fileUtilities",
    tags=["api_v1", "fileUtilities"],
)

@fileUtilities_router.post("/duplicatRecursif", response_model=ScanDuplicatesResponse)
async def duplicatRecursif(request: Request, directory: str, file_type: str,
                          app_settings: Settings = Depends(get_settings)):

    if not os.path.exists(directory) or not os.path.isdir(directory):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": "INVALID_DIRECTORY"}
        )

    hash_map = {}
    total_files_scanned = 0

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if not filename.lower().endswith(f".{file_type.strip('.')}"):
                continue

            file_path = os.path.join(root, filename)
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


@fileUtilities_router.post("/duplicatSansRecursif", response_model=ScanDuplicatesResponse)
async def duplicatSansRecursif(request: Request, directory: str, file_type: str,
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

@fileUtilities_router.post("/largeFiles", response_model=LargeFilesResponse)
async def largeFiles(request: Request, directory: str, top_n: int = 10,
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


@fileUtilities_router.post("/searchFiles", response_model=SearchFilesResponse)
async def searchFiles(request: Request, directory: str, file_type: str = "*",
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



#@fileUtilities_router.post("/convertPdfToBw", response_model=ConvertPDFResponse)
# async def convertPdfToBw(request: Request, 
#                     input_folder: str = "/media/barribar/NewDisc/PDF/Tafassir/AFaire/A_unlock/color_to_white/in",
#                     output_folder: str = "/media/barribar/NewDisc/PDF/Tafassir/AFaire/A_unlock/color_to_white/out",
#                     dpi: int = 150,
#                     app_settings: Settings = Depends(get_settings)):
    
#     try:
#         from pdf2image import convert_from_path
#         from PIL import Image
#     except ImportError:
#         return JSONResponse(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             content={"signal": "PDF2IMAGE_OR_PILLOW_NOT_INSTALLED"}
#         )

#     if not os.path.exists(input_folder) or not os.path.isdir(input_folder):
#         return JSONResponse(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             content={"signal": "INVALID_INPUT_FOLDER"}
#         )

#     os.makedirs(output_folder, exist_ok=True)

#     results = []
#     total_converted = 0
#     total_failed = 0

#     for filename in os.listdir(input_folder):
#         if not filename.lower().endswith(".pdf"):
#             continue

#         file_path = os.path.join(input_folder, filename)
#         output_path = os.path.join(output_folder, filename)

#         try:
#             # Step 1: Convert PDF pages to images
#             images = convert_from_path(file_path, dpi=dpi)

#             # Step 2: Convert images to grayscale
#             bw_images = [img.convert("L") for img in images]

#             # Step 3: Save as new PDF
#             bw_images[0].save(output_path, save_all=True, append_images=bw_images[1:])

#             results.append(ConvertPDFResult(
#                 filename=filename,
#                 status="converted",
#                 message="Converti en noir et blanc avec succès"
#             ))
#             total_converted += 1

#         except Exception as e:
#             results.append(ConvertPDFResult(
#                 filename=filename,
#                 status="error",
#                 message=str(e)
#             ))
#             total_failed += 1

#     return ConvertPDFResponse(
#         signal="CONVERT_SUCCESS",
#         input_folder=input_folder,
#         output_folder=output_folder,
#         dpi=dpi,
#         total_found=len(results),
#         total_converted=total_converted,
#         total_failed=total_failed,
#         results=results,
#     )

# @fileUtilities_router.post("/convertPdfToBw", response_model=ConvertPDFResponse)
# async def convertPdfToBw(
#     request: Request,
#     input_folder: str = "/media/barribar/NewDisc/PDF/Tafassir/AFaire/A_unlock/color_to_white/in",
#     output_folder: str = "/media/barribar/NewDisc/PDF/Tafassir/AFaire/A_unlock/color_to_white/out",
#     dpi: int = 600,
#     app_settings: Settings = Depends(get_settings),
# ):

#     if not os.path.isdir(input_folder):
#         return JSONResponse(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             content={"signal": "INVALID_INPUT_FOLDER"},
#         )

#     os.makedirs(output_folder, exist_ok=True)

#     results = []
#     total_converted = 0
#     total_failed = 0

#     for filename in os.listdir(input_folder):

#         if not filename.lower().endswith(".pdf"):
#             continue

#         file_path = os.path.join(input_folder, filename)
#         output_path = os.path.join(output_folder, filename)

#         try:

#             # 1️⃣ Convertir PDF -> images
#             images = convert_from_path(file_path, dpi=dpi)

#             if not images:
#                 raise Exception("PDF vide")

#             bw_images = []

#             for img in images:
#                 # 2️⃣ Convertir en noir/blanc optimisé
#                 gray = img.convert("L")

#                 # seuillage pour vrai noir/blanc
#                 bw = gray.point(lambda x: 0 if x < 180 else 255, "1")

#                 bw_images.append(bw)

#             # 3️⃣ Sauvegarde PDF compressé
#             bw_images[0].save(
#                 output_path,
#                 "PDF",
#                 resolution=dpi,
#                 save_all=True,
#                 append_images=bw_images[1:],
#                 optimize=True,
#             )

#             results.append({
#                 "filename": filename,
#                 "status": "converted",
#                 "message": "Conversion réussie"
#             })

#             total_converted += 1

#         except Exception as e:

#             results.append({
#                 "filename": filename,
#                 "status": "error",
#                 "message": str(e)
#             })

#             total_failed += 1

#     return {
#         "signal": "CONVERT_SUCCESS",
#         "input_folder": input_folder,
#         "output_folder": output_folder,
#         "dpi": dpi,
#         "total_found": total_converted + total_failed,
#         "total_converted": total_converted,
#         "total_failed": total_failed,
#         "results": results,
#     }


