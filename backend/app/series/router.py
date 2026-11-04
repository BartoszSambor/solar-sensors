from fastapi import APIRouter, HTTPException, status

from ..dependencies import DbSession, login_required
from .models import Series
from .schemas import SeriesCreate, SeriesRead
from .service import series_service

router = APIRouter()


def _get_series_or_404(db: DbSession, series_id: int) -> Series:
    series = series_service.get_series(db, series_id)
    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Series not found"
        )
    return series


def _check_name_free(db: DbSession, name: str, series_id: int | None = None) -> None:
    existing = series_service.get_series_by_name(db, name)
    if existing and existing.id != series_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Series name already exists"
        )


@router.get("", response_model=list[SeriesRead])
def list_series(db: DbSession) -> list[Series]:
    return list(series_service.list_series(db))


@router.post(
    "",
    response_model=SeriesRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[login_required],
)
def create_series(series_in: SeriesCreate, db: DbSession) -> Series:
    _check_name_free(db, series_in.name)
    return series_service.create_series(db, series_in)


@router.get("/{series_id}", response_model=SeriesRead)
def get_series(series_id: int, db: DbSession) -> Series:
    return _get_series_or_404(db, series_id)


@router.put("/{series_id}", response_model=SeriesRead, dependencies=[login_required])
def update_series(series_id: int, series_in: SeriesCreate, db: DbSession) -> Series:
    series = _get_series_or_404(db, series_id)
    _check_name_free(db, series_in.name, series_id)
    return series_service.update_series(db, series, series_in)


@router.delete(
    "/{series_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[login_required],
)
def delete_series(series_id: int, db: DbSession) -> None:
    """Deletes the series together with all its sensors and measurements."""
    series_service.delete_series(db, _get_series_or_404(db, series_id))
