from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.db_schemes.pdffile.schemes.pdfFileDatabase import pdfFileDatabase


class PdfFileModel:

    def __init__(self, db_client):
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client):
        return cls(db_client)

    async def get_all(self):
        async with self.db_client() as session:
            async with session.begin():
                result = await session.execute(select(pdfFileDatabase))
                return result.scalars().all()

    async def get_by_path(self, path: str):
        async with self.db_client() as session:
            async with session.begin():
                result = await session.execute(
                    select(pdfFileDatabase).where(pdfFileDatabase.pdfFile_path == path)
                )
                return result.scalar_one_or_none()

    async def insert_one(self, filename: str, path: str, file_type: str,
                         size: int, author: str = None):
        async with self.db_client() as session:
            async with session.begin():
                record = pdfFileDatabase(
                    pdfFile_name=filename,
                    pdfFile_path=path,
                    pdfFile_author=author,
                    pdfFile_type=file_type,
                    pdfFile_size=size,
                )
                session.add(record)
                await session.commit()
                return record