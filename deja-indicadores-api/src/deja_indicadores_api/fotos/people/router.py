"""Rotas de Pessoas do Deja Fotos."""

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Path,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from deja_indicadores_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_indicadores_api.fotos.people.dependencies import (
    FotosPersonAvatarServiceDependency,
    FotosPersonServiceDependency,
)
from deja_indicadores_api.fotos.people.schemas import (
    FotosPersonCreate,
    FotosPersonListResponse,
    FotosPersonMediaLink,
    FotosPersonMediaListResponse,
    FotosPersonResponse,
    FotosPersonUpdate,
)
from deja_indicadores_api.module_management.dependencies import (
    require_module,
    require_module_roles,
)
from deja_indicadores_api.user_management.models import UserModuleRole

router = APIRouter(
    prefix="/fotos/people",
    tags=["Deja Fotos - Pessoas"],
    dependencies=[Depends(require_module("fotos"))],
)

PersonId = Annotated[
    str,
    Path(min_length=36, max_length=36),
]

MediaId = Annotated[
    str,
    Path(min_length=36, max_length=36),
]

PersonReader = Annotated[
    AuthenticatedUser,
    Depends(
        require_module_roles(
            "fotos",
            UserModuleRole.MANAGER,
            UserModuleRole.VIEWER,
        )
    ),
]

PersonEditor = Annotated[
    AuthenticatedUser,
    Depends(
        require_module_roles(
            "fotos",
            UserModuleRole.MANAGER,
        )
    ),
]

PersonManager = Annotated[
    AuthenticatedUser,
    Depends(
        require_module_roles(
            "fotos",
            UserModuleRole.MANAGER,
        )
    ),
]


@router.get("", response_model=FotosPersonListResponse)
def list_people(
    service: FotosPersonServiceDependency,
    current_user: PersonReader,
    organization_id: str | None = Query(default=None),
    tenant_id: str | None = Query(default=None),
    environment_id: str | None = Query(default=None),
    active: bool | None = Query(default=None),
    name: str | None = Query(default=None, max_length=150),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
) -> FotosPersonListResponse:
    """Lista uma página de pessoas do escopo autorizado."""

    items, total = service.list(
        current_user,
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        active=active,
        name=name,
        page=page,
        page_size=page_size,
    )

    return FotosPersonListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post(
    "",
    response_model=FotosPersonResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_person(
    payload: FotosPersonCreate,
    service: FotosPersonServiceDependency,
    current_user: PersonEditor,
) -> FotosPersonResponse:
    """Cadastra uma pessoa no ambiente informado."""

    return service.create(payload, current_user)


@router.get(
    "/{person_id}/media",
    response_model=FotosPersonMediaListResponse,
)
def list_person_media(
    person_id: PersonId,
    service: FotosPersonServiceDependency,
    current_user: PersonReader,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
) -> FotosPersonMediaListResponse:
    """Lista uma página das mídias da pessoa."""

    items, total = service.list_media(
        person_id,
        current_user,
        page=page,
        page_size=page_size,
    )

    return FotosPersonMediaListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post(
    "/{person_id}/media",
    status_code=status.HTTP_204_NO_CONTENT,
)
def link_person_media(
    person_id: PersonId,
    payload: FotosPersonMediaLink,
    service: FotosPersonServiceDependency,
    current_user: PersonManager,
) -> None:
    """Vincula uma mídia à pessoa no mesmo ambiente."""

    service.link_media(
        person_id,
        payload.media_id,
        current_user,
    )


@router.delete(
    "/{person_id}/media/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def unlink_person_media(
    person_id: PersonId,
    media_id: MediaId,
    service: FotosPersonServiceDependency,
    current_user: PersonManager,
) -> None:
    """Remove um vínculo entre pessoa e mídia."""

    service.unlink_media(
        person_id,
        media_id,
        current_user,
    )


@router.get("/{person_id}/avatar")
def get_person_avatar(
    person_id: PersonId,
    avatar_service: FotosPersonAvatarServiceDependency,
    current_user: PersonReader,
) -> FileResponse:
    """Retorna o avatar WebP da pessoa autorizada."""

    return FileResponse(
        avatar_service.get_file(person_id, current_user),
        media_type="image/webp",
    )


@router.put(
    "/{person_id}/avatar",
    response_model=FotosPersonResponse,
)
async def upload_person_avatar(
    person_id: PersonId,
    file: Annotated[UploadFile, File()],
    avatar_service: FotosPersonAvatarServiceDependency,
    current_user: PersonEditor,
) -> FotosPersonResponse:
    """Substitui o avatar da pessoa por uma imagem válida."""

    return await avatar_service.upload(
        person_id,
        file,
        current_user,
    )


@router.delete(
    "/{person_id}/avatar",
    response_model=FotosPersonResponse,
)
def remove_person_avatar(
    person_id: PersonId,
    avatar_service: FotosPersonAvatarServiceDependency,
    current_user: PersonEditor,
) -> FotosPersonResponse:
    """Remove o avatar sem afetar fotos ou reconhecimento."""

    return avatar_service.remove(person_id, current_user)


@router.get("/{person_id}", response_model=FotosPersonResponse)
def get_person(
    person_id: PersonId,
    service: FotosPersonServiceDependency,
    current_user: PersonReader,
) -> FotosPersonResponse:
    """Consulta uma pessoa do escopo autorizado."""

    return service.find_by_id(person_id, current_user)


@router.put("/{person_id}", response_model=FotosPersonResponse)
def update_person(
    person_id: PersonId,
    payload: FotosPersonUpdate,
    service: FotosPersonServiceDependency,
    current_user: PersonEditor,
) -> FotosPersonResponse:
    """Atualiza uma pessoa sem mudar seu ambiente."""

    return service.update(person_id, payload, current_user)


@router.delete(
    "/{person_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_person(
    person_id: PersonId,
    avatar_service: FotosPersonAvatarServiceDependency,
    current_user: PersonManager,
) -> None:
    """Exclui pessoa, vínculos e avatar."""

    avatar_service.delete_person(person_id, current_user)