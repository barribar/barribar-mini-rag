from fastapi import FastAPI
from routes import ( base, data, nlp, fileUtilities, pdfFile, telegramFile)
# from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templatess.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


app = FastAPI()

async def startup_span():
    settings = get_settings()

    #app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    #app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRESS_USERNAME}:{settings.POSTGRESS_PASSWORD}@{settings.POSTGRESS_HOSTS}:{settings.POSTGRESS_PORT}/{settings.POSTGRESS_MAIN_DATABASE}"
    app.db_engine = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(
        app.db_engine, class_=AsyncSession, expire_on_commit=False,
    )

    postgres_pdf_conn = f"postgresql+asyncpg://{settings.POSTGRESS_USERNAME}:{settings.POSTGRESS_PASSWORD}@{settings.POSTGRESS_HOSTS}:{settings.POSTGRESS_PORT}/{settings.POSTGRESS_PDF_DATABASE}"
    app.pdf_db_engine = create_async_engine(postgres_pdf_conn)
    app.pdf_db_client = sessionmaker(
        app.pdf_db_engine, class_=AsyncSession, expire_on_commit=False,
    )

    postgres_telegram_conn = f"postgresql+asyncpg://{settings.POSTGRESS_USERNAME}:{settings.POSTGRESS_PASSWORD}@{settings.POSTGRESS_HOSTS}:{settings.POSTGRESS_PORT}/{settings.POSTGRESS_TELEGRAM_DATABASE}"
    app.telegram_db_engine = create_async_engine(postgres_telegram_conn)
    app.telegram_db_client = sessionmaker(
    app.telegram_db_engine, class_=AsyncSession, expire_on_commit=False,
    )
    
    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(config=settings, db_client=app.db_client)

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    # vector db client
    app.vectordb_client = vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )
    await app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )


async def shutdown_span():
    # app.mongo_conn.close()
    await app.db_engine.dispose()
    await app.pdf_db_engine.dispose()
    await app.telegram_db_engine.dispose()
    
    await app.vectordb_client.disconnect()

    # await app.pdf_db_engine.async_dispose()

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
app.include_router(fileUtilities.fileUtilities_router)
app.include_router(pdfFile.pdfFile_router)
app.include_router(telegramFile.telegramFile_router)