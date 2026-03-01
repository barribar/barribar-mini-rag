from pydantic import BaseModel

class N8NProcessRequest(BaseModel):
    project_id: int
    file_id: str | None = None
    chunk_size: int = 1000
    overlap_size: int = 100
    do_reset: int = 0