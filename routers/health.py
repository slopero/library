from fastapi import APIRouter

from schemas.health import HealthResponse
from services.health import get_health

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
def health() -> HealthResponse:
    return get_health()
