from fastapi import APIRouter, Depends, Query

from api.auth import verify_api_key
from api.dependencies import get_db_connection
from api.models.pipeline import PipelineHealth, PipelineRun
from db.pipeline_health import (
    get_pipeline_health,
    get_recent_pipeline_runs,
)


router = APIRouter(
    prefix="/pipeline",
    tags=["Pipeline"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/health", response_model=PipelineHealth)
def pipeline_health(conn=Depends(get_db_connection)):
    try:
        return get_pipeline_health(conn)
    finally:
        conn.close()


@router.get("/runs", response_model=list[PipelineRun])
def recent_pipeline_runs(
    limit: int = Query(default=10, ge=1, le=100),
    conn=Depends(get_db_connection),
):
    try:
        return get_recent_pipeline_runs(conn, limit=limit)
    finally:
        conn.close()