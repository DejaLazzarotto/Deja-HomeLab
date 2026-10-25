"""Endpoints autenticados da biblioteca musical VIVARO."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from deja_platform_api.core.config import Settings, get_settings
from deja_platform_api.fotos.music.library import VivaroMusicLibrary
from deja_platform_api.module_management.dependencies import (
    require_module,
    require_module_roles,
)
from deja_platform_api.user_management.models import UserModuleRole

router = APIRouter(
    prefix="/fotos/music",
    tags=["VIVARO - Música"],
    dependencies=[
        Depends(require_module("fotos")),
        Depends(
            require_module_roles(
                "fotos",
                UserModuleRole.MANAGER,
                UserModuleRole.VIEWER,
            )
        ),
    ],
)


def get_music_library(
    settings: Annotated[Settings, Depends(get_settings)],
) -> VivaroMusicLibrary:
    return VivaroMusicLibrary(settings.vivaro_music_dir)


MusicLibraryDependency = Annotated[
    VivaroMusicLibrary,
    Depends(get_music_library),
]


@router.get("")
def list_music(
    library: MusicLibraryDependency,
) -> dict[str, list[str]]:
    """Lista as faixas disponíveis."""
    return {"tracks": library.list_tracks()}


@router.get("/{filename}")
def get_music(
    filename: str,
    library: MusicLibraryDependency,
) -> FileResponse:
    """Entrega uma faixa da biblioteca autorizada."""
    try:
        path = library.resolve_track(filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return FileResponse(
        path=path,
        media_type="audio/mpeg",
        content_disposition_type="inline",
    )
