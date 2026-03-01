# FastAPI + n8n + Docker Stack

## 1️⃣ .env

```env
# ----------------------
# App & LLM
# ----------------------
APP_NAME=mini-RAG
APP_VERSION=0.1

OPENAI_API_KEY=
OPENAI_API_URL=
COHERE_API_KEY=

FILE_ALLOWED_TYPES=text/plain,application/pdf
FILE_MAX_SIZE=10
FILE_DEFAULT_CHUNK_SIZE=512000

POSTGRESS_USERNAME=postgres
POSTGRESS_PASSWORD=postgres
POSTGRESS_HOSTS=pgvector
POSTGRESS_PORT=5432
POSTGRESS_MAIN_DATABASE=minirag

# ----------------------
# MongoDB
# ----------------------
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=admin
MONGODB_DATABASE=mini-rag

# ----------------------
# n8n
# ----------------------
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin123
N8N_ENCRYPTION_KEY=3xY9KpLmQ8vW2zT6nB4rC7aS5dF1hJ0k
N8N_HOST=n8n
N8N_PORT=5678
WEBHOOK_URL=http://n8n:5678/
GENERIC_TIMEZONE=Africa/Casablanca
N8N_SECRET=super_secret_token_123

# ----------------------
# LLM
# ----------------------
GENERATION_BACKEND=OPENAI
EMBEDDING_BACKEND=COHERE
GENERATION_MODEL_ID_LITERAL=llama3.2:latest,gpt-3.5-turbo,command-r-plus-08-2024
GENERATION_MODEL_ID=llama3.2:latest
EMBEDDING_MODEL_ID=embed-multilingual-light-v3.0
EMBEDDING_MODEL_SIZE=384
INPUT_DAFAULT_MAX_CHARACTERS=1024
GENERATION_DAFAULT_MAX_TOKENS=200
GENERATION_DAFAULT_TEMPERATURE=0.1

VECTOR_DB_BACKEND_LITERAL=QDRANT,PGVECTOR
VECTOR_DB_BACKEND=PGVECTOR
VECTOR_DB_PATH=pgvector_data
VECTOR_DB_DISTANCE_METHOD=cosine
VECTOR_DB_PGVEC_INDEX_THRESHOLD=100

PRIMARY_LANG=ar
DEFAULT_LANG=en
```

## 2️⃣ docker-compose.yml

```yaml
version: "3.9"

services:
  mongodb:
    image: mongo:7-jammy
    container_name: mongodb
    ports:
      - "27007:27017"
    volumes:
      - mongodata:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=${MONGO_INITDB_ROOT_USERNAME}
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD}
    networks:
      - backend
    restart: always

  pgvector:
    image: pgvector/pgvector:0.8.0-pg17
    container_name: pgvector
    ports:
      - "5400:5432"
    volumes:
      - pgvector_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=${POSTGRESS_USERNAME}
      - POSTGRES_PASSWORD=${POSTGRESS_PASSWORD}
      - POSTGRES_DB=${POSTGRESS_MAIN_DATABASE}
    networks:
      - backend
    restart: always

  api:
    build: .
    container_name: fastapi
    ports:
      - "5000:5000"
    environment:
      - POSTGRESS_USERNAME=${POSTGRESS_USERNAME}
      - POSTGRESS_PASSWORD=${POSTGRESS_PASSWORD}
      - POSTGRESS_HOSTS=pgvector
      - POSTGRESS_PORT=5432
      - POSTGRESS_MAIN_DATABASE=${POSTGRESS_MAIN_DATABASE}
      - MONGODB_URL=mongodb://admin:${MONGO_INITDB_ROOT_PASSWORD}@mongodb:27017
      - MONGODB_DATABASE=${MONGODB_DATABASE}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - COHERE_API_KEY=${COHERE_API_KEY}
      - VECTOR_DB_BACKEND=${VECTOR_DB_BACKEND}
      - VECTOR_DB_PATH=${VECTOR_DB_PATH}
      - VECTOR_DB_DISTANCE_METHOD=${VECTOR_DB_DISTANCE_METHOD}
    networks:
      - backend
    restart: always
    command: >
      uvicorn main:app
      --host 0.0.0.0
      --port 5000
      --reload

  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - N8N_HOST=n8n
      - N8N_PORT=5678
      - WEBHOOK_URL=${WEBHOOK_URL}
      - GENERIC_TIMEZONE=${GENERIC_TIMEZONE}
      - N8N_SECRET=${N8N_SECRET}
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - backend
    restart: always

networks:
  backend:

volumes:
  mongodata:
  pgvector_data:
  n8n_data:
```

## 3️⃣ FastAPI structure

```text
project/
│
├─ main.py
├─ helpers/
│   ├─ config.py
│   └─ auth.py
├─ routes/
│   ├─ base.py
│   └─ data.py
├─ schemas/
│   └─ n8n.py
├─ controllers/
│   └─ ProcessController.py
├─ models/
│   ├─ ProjectModel.py
│   ├─ AssetModel.py
│   ├─ ChunkModel.py

---------------------------------------------------------------------
## routes/base.py (ta route existante)
from fastapi import APIRouter, Depends
from helpers.config import get_settings, Settings

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)

@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):
    return {
        "app_name": app_settings.APP_NAME,
        "app_version": app_settings.APP_VERSION,
    }

-----------------------------------------------------------------------
## main.py

from fastapi import FastAPI
from routes import base, data
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templatess.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# -----------------------------
# Startup / Shutdown events
# -----------------------------
async def startup_span():
    settings = get_settings()

    # Postgres
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRESS_USERNAME}:{settings.POSTGRESS_PASSWORD}@{settings.POSTGRESS_HOSTS}:{settings.POSTGRESS_PORT}/{settings.POSTGRESS_MAIN_DATABASE}"
    app.db_engine = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(
        app.db_engine, class_=AsyncSession, expire_on_commit=False,
    )

    # LLM providers
    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(settings)

    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    app.vectordb_client = vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )

async def shutdown_span():
    app.db_engine.dispose()
    app.vectordb_client.disconnect()

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

# -----------------------------
# Routers
# -----------------------------
app.include_router(base.base_router)   # Route "/api/v1/"
app.include_router(data.data_router)   # Routes "/api/v1/data/*"

-------------------------------------------------------------------

## schemas/n8n.py (Pydantic payload)

from pydantic import BaseModel, Field
from typing import Optional

class N8NProcessPayload(BaseModel):
    project_id: int = Field(..., description="ID du projet à traiter")
    chunk_size: Optional[int] = Field(512, description="Taille des chunks")
    overlap_size: Optional[int] = Field(50, description="Taille du chevauchement")
    do_reset: Optional[int] = Field(0, description="Supprimer anciens chunks si 1")
    file_id: Optional[str] = Field(None, description="ID du fichier (optionnel)")

-------------------------------------------------------------------
## helpers/auth.py

from fastapi import Request, HTTPException
from helpers.config import get_settings

settings = get_settings()

async def verify_n8n_key(request: Request):
    key = request.headers.get("x-api-key")
    if key != settings.N8N_SECRET:
        raise HTTPException(status_code=403, detail="Invalid API Key")

## -------------------------------------------------------------------

## routes/data.py (upload, process et n8n)

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from helpers.auth import verify_n8n_key
from schemas.n8n import N8NProcessPayload
from controllers import ProcessController, ProjectController, DataController
from models.ChunkModel import ChunkModel
from models.ProjectModel import ProjectModel
from models.AssetModel import AssetModel
from models.db_schemes import DataChunk
from models.enums.AssetTypeEnum import AssetTypeEnum

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

# -----------------------------
# Route n8n
# -----------------------------
@data_router.post("/n8n/process")
async def n8n_process(
    payload: N8NProcessPayload,
    request: Request,
    auth=Depends(verify_n8n_key)
):
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=payload.project_id)

    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
    project_files_ids = {}

    if payload.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.project_id,
            asset_name=payload.file_id
        )
        if asset_record is None:
            return JSONResponse(status_code=400, content={"signal": "FILE_ID_ERROR"})
        project_files_ids = {asset_record.asset_id: asset_record.asset_name}
    else:
        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.project_id,
            asset_type=AssetTypeEnum.FILE.value
        )
        project_files_ids = {r.asset_id: r.asset_name for r in project_files}

    if not project_files_ids:
        return JSONResponse(status_code=400, content={"signal": "NO_FILES_ERROR"})

    process_controller = ProcessController(project_id=project.project_id)
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    if payload.do_reset:
        await chunk_model.delete_chunks_by_project_id(project_id=project.project_id)

    total_chunks = 0
    total_files = 0

    for asset_id, file_name in project_files_ids.items():
        content = process_controller.get_file_content(file_id=file_name)
        if not content:
            continue
        chunks = process_controller.process_file_content(
            file_content=content,
            file_id=file_name,
            chunk_size=payload.chunk_size,
            overlap_size=payload.overlap_size
        )
        if not chunks:
            continue

        chunk_records = [
            DataChunk(
                chunk_text=c.page_content,
                chunk_metadata=c.metadata,
                chunk_order=i + 1,
                chunk_project_id=project.project_id,
                chunk_asset_id=asset_id
            ) for i, c in enumerate(chunks)
        ]

        inserted = await chunk_model.insert_many_chunks(chunks=chunk_records)
        total_chunks += inserted
        total_files += 1

    return JSONResponse(
        content={
            "signal": "PROCESSING_SUCCESS",
            "processed_files": total_files,
            "inserted_chunks": total_chunks
        }
    )


