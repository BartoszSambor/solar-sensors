from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query

from ..dependencies import DbSession
from . import schemas as user_schemas
from .service import user_service

router = APIRouter()


@router.get("/", response_model=user_schemas.UserListResponse)
def list_users(
    db: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    username: str | None = Query(None),
    created_at_from: Annotated[
        datetime | None,
        Query(description="Filter users created on or after this datetime"),
    ] = None,
    created_at_to: Annotated[
        datetime | None,
        Query(description="Filter users created on or before this datetime"),
    ] = None,
    sort_field: str = Query("id"),
    sort_direction: str = Query("asc"),
) -> user_schemas.UserListResponse:
    filters = user_schemas.UserFilter(
        username=username,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
    )
    sort = user_schemas.UserSort(field=sort_field, direction=sort_direction)
    return user_service.list_users(
        db=db,
        skip=skip,
        limit=limit,
        filters=filters,
        sort=sort,
    )
