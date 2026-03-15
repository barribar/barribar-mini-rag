from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from routes.schemes.telegramFileFr import (
    InsertTelegramFilesResponseFr, TelechargerTelegramResponseFr
)
from models.TelegramFrModel import TelegramFrModel
import os
import logging
from datetime import datetime
from typing import List

logger = logging.getLogger('uvicorn.error')

telegramFileFr_router = APIRouter(
    prefix="/api/v1/telegramFileFr",
    tags=["api_v1", "telegramFileFr"],
)


@telegramFileFr_router.post("/scan-and-upload", response_model=InsertTelegramFilesResponseFr)
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
    telegram_model = await TelegramFrMode.create_instance(
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

    return InsertTelegramFilesResponseFr(
        signal="UPLOAD_SUCCESS",
        total_scanned=total_scanned,
        total_inserted=total_inserted,
        total_skipped=total_skipped,
        total_failed=total_failed,
    )


@telegramFileFr_router.post("/telecharger_one_maktaba_fr", response_model=TelechargerTelegramResponseFr)
async def telecharger_one_maktaba_fr(request: Request,
                                    maktaba_id: int,
                                    app_settings: Settings = Depends(get_settings)):

    telegram_model = await TelegramFrMode.create_instance(
        db_client=request.app.telegram_db_client
    )

    # Récupère la maktaba et son channel
    maktaba = await telegram_model.get_maktaba_by_id(maktaba_id)
    if not maktaba:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": "MAKTABA_NOT_FOUND"}
        )

    # channel = maktaba.maktaba_at if maktaba.maktaba_at else maktaba.maktaba_link
    # Si maktaba_at est un nombre, utilise-le directement comme int
    try:
        int(maktaba.maktaba_at)
        channel = maktaba.maktaba_link
    except (ValueError, TypeError):
        channel = f"@{maktaba.maktaba_at}"

    # Init Telethon
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

    total_inserted = 0
    total_skipped = 0
    total_failed = 0

    try:
        # Récupère le dernier kitab_id dans la DB pour cette maktaba
        last_id_in_db = await telegram_model.get_last_kitab_id(maktaba_id)

        # Récupère le dernier message_id dans le channel Telegram
        last_id_in_channel = None
        async for msg in client.iter_messages(channel, limit=1):
            last_id_in_channel = msg.id

        if last_id_in_channel is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": "CHANNEL_EMPTY_OR_NOT_FOUND"}
            )

        # Calcule le nombre de nouveaux messages à récupérer
        if last_id_in_db is None:
            limit = None  # Tout télécharger
        else:
            limit = last_id_in_channel - last_id_in_db
            if limit <= 0:
                return TelechargerTelegramResponseFr(
                    signal="ALREADY_UP_TO_DATE",
                    maktaba_id=maktaba_id,
                    channel=str(channel),
                    total_inserted=0,
                    total_skipped=0,
                    total_failed=0,
                )

        logger.info(f"Limite : {limit} nouveaux messages à récupérer")

        # Parcourt les messages du channel
        try:
            # async for message in client.iter_messages(channel, limit=limit):
            async for message in client.iter_messages(channel, min_id=last_id_in_db or 0):
                try:
                    # Vérifie que le message contient un document
                    if not (hasattr(message, 'media') and hasattr(message.media, 'document')):
                        continue

                    mime_type = message.media.document.mime_type
                    # if mime_type == 'image/webp':
                    #     continue
                    if mime_type != 'application/pdf':
                        continue

                    # Titre du fichier
                    title = message.file.name if message.file and message.file.name else str(message.id)
                    title = os.path.splitext(title)[0]  # Enlève l'extension

                    # Lien du message
                    if message.reply_to_msg_id is None:
                        kitab_link = str(message.id)
                    else:
                        kitab_link = f"{message.reply_to_msg_id}/{message.id}"

                    # Vérifie si déjà dans la DB
                    existing = await telegram_model.get_kitab_by_title(maktaba_id, title)
                    if existing:
                        total_skipped += 1
                        continue

                    # Insère dans la DB
                    await telegram_model.insert_kitab(
                        maktaba_id=maktaba_id,
                        title=title,
                        kitab_link=kitab_link,
                        kitab_size=message.file.size if message.file else 0,
                        kitab_date=str(message.date),
                        kitab_message=message.message.replace("\n", " ** ") if message.message else "",
                        kitab_group="",
                    )

                    total_inserted += 1
                    logger.info(f"[{total_inserted}] Inséré : {title}")

                except Exception as e:
                    logger.error(f"Erreur sur message {message.id}: {e}")
                    total_failed += 1

        except Exception as e:
            logger.error(f"Erreur channel {channel}: {e}")
            return TelechargerTelegramResponseFr(
                signal=f"CHANNEL_ERROR: {str(e)}",
                maktaba_id=maktaba_id,
                channel=str(channel),
                total_inserted=0,
                total_skipped=0,
                total_failed=0,
            )

    finally:
        await client.disconnect()

    return TelechargerTelegramResponseFr(
        signal="DOWNLOAD_SUCCESS",
        maktaba_id=maktaba_id,
        channel=str(channel),
        total_inserted=total_inserted,
        total_skipped=total_skipped,
        total_failed=total_failed,
    )


@telegramFileFr_router.post("/telecharger_all_maktabat_fr", response_model=List[TelechargerTelegramResponseFr])
async def telecharger_all_maktabat_fr(request: Request,
                                   app_settings: Settings = Depends(get_settings)):

    telegram_model = await TelegramFrMode.create_instance(
        db_client=request.app.telegram_db_client
    )

    # Récupère toutes les maktabas
    all_maktabat = await telegram_model.get_all_maktabat()
    if not all_maktabat:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": "NO_MAKTABAT_FOUND"}
        )

    results = []

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

    try:
        for maktaba in all_maktabat:
            try:
                int(maktaba.maktaba_at)
                channel = maktaba.maktaba_link
            except (ValueError, TypeError):
                channel = f"@{maktaba.maktaba_at}"



            total_inserted = 0
            total_skipped = 0
            total_failed = 0

            try:
                last_id_in_db = await telegram_model.get_last_kitab_id(maktaba.maktaba_id)

                last_id_in_channel = None
                async for msg in client.iter_messages(channel, limit=1):
                    last_id_in_channel = msg.id

                if last_id_in_channel is None:
                    logger.error(f"Channel vide ou introuvable : {channel}")
                    results.append(TelechargerTelegramResponseFr(
                        signal="CHANNEL_EMPTY_OR_NOT_FOUND",
                        maktaba_id=maktaba.maktaba_id,
                        channel=channel,
                        total_inserted=0,
                        total_skipped=0,
                        total_failed=0,
                    ))
                    continue

                if last_id_in_db is None:
                    limit = None
                else:
                    limit = last_id_in_channel - last_id_in_db
                    if limit <= 0:
                        results.append(TelechargerTelegramResponseFr(
                            signal="ALREADY_UP_TO_DATE",
                            maktaba_id=maktaba.maktaba_id,
                            channel=channel,
                            total_inserted=0,
                            total_skipped=0,
                            total_failed=0,
                        ))
                        continue

                async for message in client.iter_messages(channel, limit=limit):
                    try:
                        if not (hasattr(message, 'media') and hasattr(message.media, 'document')):
                            continue

                        mime_type = message.media.document.mime_type
                        #if mime_type == 'image/webp':
                        #    continue
                        if mime_type != 'application/pdf':
                            continue

                        title = message.file.name if message.file and message.file.name else str(message.id)
                        title = os.path.splitext(title)[0]

                        if message.reply_to_msg_id is None:
                            kitab_link = str(message.id)
                        else:
                            kitab_link = f"{message.reply_to_msg_id}/{message.id}"

                        existing = await telegram_model.get_kitab_by_title(maktaba.maktaba_id, title)
                        if existing:
                            total_skipped += 1
                            continue

                        await telegram_model.insert_kitab(
                            maktaba_id=maktaba.maktaba_id,
                            kitab_id=message.id,
                            title=title,
                            kitab_link=kitab_link,
                            kitab_size=message.file.size if message.file else 0,
                            kitab_date=str(message.date),
                            kitab_message=message.message.replace("\n", " ** ") if message.message else "",
                            kitab_group="",
                        )
                        total_inserted += 1
                        logger.info(f"[{maktaba.maktaba_id}] [{total_inserted}] Inséré : {title}")

                    except Exception as e:
                        logger.error(f"Erreur message {message.id}: {e}")
                        total_failed += 1

            except Exception as e:
                logger.error(f"Erreur channel {channel}: {e}")
                results.append(TelechargerTelegramResponseFr(
                    signal=f"CHANNEL_ERROR: {str(e)}",
                    maktaba_id=maktaba.maktaba_id,
                    channel=channel,
                    total_inserted=0,
                    total_skipped=0,
                    total_failed=0,
                ))
                continue

            results.append(TelechargerTelegramResponseFr(
                signal="DOWNLOAD_SUCCESS",
                maktaba_id=maktaba.maktaba_id,
                channel=channel,
                total_inserted=total_inserted,
                total_skipped=total_skipped,
                total_failed=total_failed,
            ))
            logger.info(f"Maktaba {maktaba.maktaba_id} terminée — insérés: {total_inserted}, skippés: {total_skipped}")

    finally:
        await client.disconnect()

    return results