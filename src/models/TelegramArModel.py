from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.db_schemes.telegram.schemes.telegram_base import TelegramSQLAlchemyBase
from models.db_schemes.telegram.schemes import AllTelegramMaktabaAr, AllTelegramKotobAr
from sqlalchemy import func

class TelegramArModel:

    def __init__(self, db_client):
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client):
        return cls(db_client)

    async def get_maktaba_by_id(self, maktaba_id: int):
        async with self.db_client() as session:
            async with session.begin():
                result = await session.execute(
                    select(AllTelegramMaktabaAr).where(
                        AllTelegramMaktabaAr.maktaba_id == maktaba_id
                    )
                )
                return result.scalar_one_or_none()

    async def get_kitab_by_title(self, maktaba_id: int, title: str):
        async with self.db_client() as session:
            async with session.begin():
                result = await session.execute(
                    select(AllTelegramKotobAr).where(
                        AllTelegramKotobAr.maktaba == maktaba_id,
                        AllTelegramKotobAr.kitab_title == title
                    )
                )
                return result.scalar_one_or_none()

    async def get_last_kitab_id(self, maktaba_id: int):
        """Retourne le max kitab_id dans la DB pour une maktaba donnée."""
        async with self.db_client() as session:
            async with session.begin():
                result = await session.execute(
                    select(func.max(AllTelegramKotobAr.kitab_id)).where(
                        AllTelegramKotobAr.maktaba == maktaba_id
                    )
                )
                return result.scalar_one_or_none()

    async def get_all_maktabat(self):
        async with self.db_client() as session:
            async with session.begin():
                result = await session.execute(select(AllTelegramMaktabaAr))
                return result.scalars().all()
    
    async def insert_kitab(self, maktaba_id: int,  kitab_id: int, title: str, kitab_link: str,
                           kitab_size: int, kitab_date: str = None,
                           kitab_message: str = None, kitab_group: str = None):
        async with self.db_client() as session:
            async with session.begin():
                record = AllTelegramKotobAr(
                    maktaba=maktaba_id,
                    kitab_id=kitab_id,  # ← ajoute ça
                    kitab_title=title,
                    kitab_link=kitab_link,
                    kitab_size=kitab_size,
                    kitab_date=kitab_date,
                    kitab_message=kitab_message,
                    kitab_group=kitab_group,
                )
                session.add(record)
                await session.commit()
                return record

    