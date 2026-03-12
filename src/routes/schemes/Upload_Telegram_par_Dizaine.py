# Script rapide avec uploads parallèles

import os
import asyncio
from telethon import TelegramClient

api_id = 27097109
api_hash = '7b901535c3dae1bd4217303a72659072'
session_name = 'mySession'

channel = "https://t.me/Joutiya_Library"
folder = "/media/barribar/NewDisc/PDF/python/python_django"

MAX_PARALLEL = 5   # nombre d'uploads en même temps

client = TelegramClient(session_name, api_id, api_hash)


async def upload_file(path):

    filename = os.path.basename(path)
    title = os.path.splitext(filename)[0].replace("_", " ")

    try:
        await client.send_file(
            channel,
            path,
            caption=f"📚 {title}"
        )

        print("Uploaded:", filename)

    except Exception as e:
        print("Error:", filename, e)


async def main():

    await client.start()

    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    ]

    sem = asyncio.Semaphore(MAX_PARALLEL)

    async def sem_task(file):
        async with sem:
            await upload_file(file)

    await asyncio.gather(*(sem_task(f) for f in files))


with client:
    client.loop.run_until_complete(main())