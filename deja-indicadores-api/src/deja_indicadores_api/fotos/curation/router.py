"""API de revisão facial com leitura e edição por papel."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from fastapi.responses import FileResponse

from deja_indicadores_api.authentication.dependencies import require_roles
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.fotos.curation.dependencies import CurationServiceDependency
from deja_indicadores_api.fotos.curation.schemas import (
    FaceCreate,
    FaceDecision,
    FacePage,
    FaceResponse,
    ReferencePage,
    ReferenceResponse,
)
from deja_indicadores_api.fotos.media.schemas import FotosMediaListResponse
from deja_indicadores_api.module_management.dependencies import require_module
from deja_indicadores_api.user_management.models import UserRole

router = APIRouter(
    prefix="/fotos/curation",
    tags=["Deja Fotos - Curadoria"],
    dependencies=[Depends(require_module("fotos"))],
)
ResourceId = Annotated[str, Path(min_length=36, max_length=36)]
Reader = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.MANAGER,
            UserRole.ANALYST,
            UserRole.VIEWER,
        )
    ),
]
Manager = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.MANAGER,
        )
    ),
]


@router.get("/media", response_model=FotosMediaListResponse)
def list_curation_media(
    service: CurationServiceDependency,
    user: Reader,
    environment_id: str | None = None,
    album_id: str | None = None,
    person_id: str | None = None,
    situation: str = Query("all", pattern="^(all|suggested|unknown|confirmed)$"),
    year: int | None = Query(None, ge=1900, le=2200),
    month: int | None = Query(None, ge=1, le=12),
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
) -> FotosMediaListResponse:
    items, total = service.list_media(
        user,
        environment_id=environment_id,
        album_id=album_id,
        person_id=person_id,
        situation=situation,
        year=year,
        month=month,
        page=page,
        page_size=page_size,
    )
    return FotosMediaListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/summary", response_model=dict[str, int])
def summary(
    service: CurationServiceDependency,
    user: Reader,
    environment_id: str | None = None,
) -> dict[str, int]:
    return service.summary(user, environment_id)


@router.get("/media/{media_id}/faces", response_model=FacePage)
def list_faces(
    media_id: ResourceId,
    service: CurationServiceDependency,
    user: Reader,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> FacePage:
    items, total = service.list_faces(media_id, user, page=page, page_size=page_size)
    return FacePage(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("/media/{media_id}/faces", response_model=FaceResponse, status_code=201)
def create_face(
    media_id: ResourceId,
    payload: FaceCreate,
    service: CurationServiceDependency,
    user: Manager,
) -> FaceResponse:
    return FaceResponse.model_validate(service.create(media_id, payload, user))


@router.post("/media/{media_id}/detect", response_model=list[FaceResponse])
def detect_faces(
    media_id: ResourceId,
    service: CurationServiceDependency,
    user: Manager,
) -> list[FaceResponse]:
    return [FaceResponse.model_validate(face) for face in service.detect(media_id, user)]


@router.post("/faces/{face_id}/confirm", response_model=FaceResponse)
def confirm_face(
    face_id: ResourceId,
    payload: FaceDecision,
    service: CurationServiceDependency,
    user: Manager,
) -> FaceResponse:
    return FaceResponse.model_validate(service.confirm(face_id, payload.person_id, user))


@router.post("/faces/{face_id}/reject", response_model=FaceResponse)
def reject_face(
    face_id: ResourceId,
    service: CurationServiceDependency,
    user: Manager,
) -> FaceResponse:
    return FaceResponse.model_validate(service.reject(face_id, user))


@router.delete("/faces/{face_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_face(face_id: ResourceId, service: CurationServiceDependency, user: Manager) -> None:
    service.delete(face_id, user)


@router.post("/faces/{face_id}/teach", response_model=ReferenceResponse)
def teach_face(
    face_id: ResourceId,
    service: CurationServiceDependency,
    user: Manager,
) -> ReferenceResponse:
    return ReferenceResponse.model_validate(service.teach(face_id, user))


@router.get("/people/{person_id}/references", response_model=ReferencePage)
def list_references(
    person_id: ResourceId,
    service: CurationServiceDependency,
    user: Reader,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> ReferencePage:
    items, total = service.list_references(person_id, user, page=page, page_size=page_size)
    return ReferencePage(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/references/{reference_id}/image")
def reference_image(
    reference_id: ResourceId,
    service: CurationServiceDependency,
    user: Reader,
) -> FileResponse:
    return FileResponse(service.reference_file(reference_id, user), media_type="image/webp")


@router.delete("/references/{reference_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reference(
    reference_id: ResourceId,
    service: CurationServiceDependency,
    user: Manager,
) -> None:
    service.remove_reference(reference_id, user)
