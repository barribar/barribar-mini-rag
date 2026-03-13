from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from routes.schemes.telegramFile import (
    InsertTelegramFilesResponse
)
from models.TelegramModel import TelegramModel
import os
import logging
from datetime import datetime

logger = logging.getLogger('uvicorn.error')

telegramFile_router = APIRouter(
    prefix="/api/v1/telegramFile",
    tags=["api_v1", "telegramFile"],
)


@telegramFile_router.post("/scan-and-upload", response_model=InsertTelegramFilesResponse)
async def scan_and_upload(request: Request, directory: str,
                          maktaba_id: int,
                          file_type: str = "pdf",
                          app_settings: Settings = Depends(get_settings)):

    if not os.path.exists(directory) or not os.path.isdir(directory):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": "INVALID_DIRECTORY"}
        )

    # Init Telegram model
    telegram_model = await TelegramModel.create_instance(
        db_client=request.app.telegram_db_client
    )

    # Get maktaba and its channel link
    maktaba = await telegram_model.get_maktaba_by_id(maktaba_id)
    if not maktaba:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": "MAKTABA_NOT_FOUND"}
        )

    channel = maktaba.maktaba_link

    # Init Telethon client
    try:
        from telethon import TelegramClient
        client = TelegramClient(
            app_settings.TELEGRAM_SESSION_NAME,
            app_settings.TELEGRAM_SESSION_API_ID,
            app_settings.TELEGRAM_SESSION_API_HASH
        )
        await client.start()
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": f"TELEGRAM_CLIENT_ERROR: {str(e)}"}
        )

    total_scanned = 0
    total_inserted = 0
    total_skipped = 0
    total_failed = 0

    extension = None if file_type == "*" else f".{file_type.strip('.')}"

    try:
        for filename in os.listdir(directory):
            if extension and not filename.lower().endswith(extension):
                continue

            file_path = os.path.join(directory, filename)
            if not os.path.isfile(file_path):
                continue

            total_scanned += 1
            title = os.path.splitext(filename)[0]

            try:
                # Check si déjà dans la DB
                existing = await telegram_model.get_kitab_by_title(maktaba_id, title)
                if existing:
                    logger.info(f"[SKIP] {filename} déjà dans la DB")
                    total_skipped += 1
                    continue

                # Upload vers Telegram
                size = os.path.getsize(file_path)
                message = await client.send_file(
                    channel,
                    file_path,
                    caption=title
                )

                # Récupère le lien du message
                kitab_link = f"https://t.me/{channel.split('/')[-1]}/{message.id}"

                # Insère dans la DB
                await telegram_model.insert_kitab(
                    maktaba_id=maktaba_id,
                    title=title,
                    kitab_link=kitab_link,
                    kitab_size=size,
                    kitab_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    kitab_message=title,
                    kitab_group=str(maktaba_id),
                )

                total_inserted += 1
                logger.info(f"[{total_inserted}/{total_scanned}] Uploadé et inséré : {filename}")

            except (FileNotFoundError, OSError):
                continue
            except Exception as e:
                logger.error(f"Erreur sur {filename}: {e}")
                total_failed += 1

    finally:
        await client.disconnect()

    return InsertTelegramFilesResponse(
        signal="UPLOAD_SUCCESS",
        total_scanned=total_scanned,
        total_inserted=total_inserted,
        total_skipped=total_skipped,
        total_failed=total_failed,
    )