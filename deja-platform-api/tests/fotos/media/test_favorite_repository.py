"""Testes de persistência dos favoritos individuais."""

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session, sessionmaker

from deja_platform_api.fotos.media.favorite_models import (
    FotosMediaFavoriteModel,
)
from deja_platform_api.fotos.media.favorite_repository import (
    FotosMediaFavoriteRepository,
)
from deja_platform_api.fotos.media.models import FotosMediaModel


@pytest.fixture()
def favorite_repository(
    test_session_factory: sessionmaker[Session],
):
    """Fornece um repositório conectado ao banco de testes."""

    with test_session_factory() as session:
        yield FotosMediaFavoriteRepository(session)


def test_favorite_model_has_expected_table() -> None:
    """Confirma o mapeamento básico da tabela."""

    assert FotosMediaFavoriteModel.__tablename__ == (
        "fotos_media_favorites"
    )

    columns = {
        column.name
        for column in FotosMediaFavoriteModel.__table__.columns
    }

    assert columns == {
        "id",
        "user_id",
        "media_id",
        "created_at",
    }


def test_unknown_favorite_returns_false(
    favorite_repository: FotosMediaFavoriteRepository,
) -> None:
    """Uma mídia não favoritada não possui vínculo."""

    assert not favorite_repository.exists(
        str(uuid4()),
        str(uuid4()),
    )


def test_unknown_favorite_returns_none(
    favorite_repository: FotosMediaFavoriteRepository,
) -> None:
    """A consulta de vínculo inexistente retorna None."""

    assert favorite_repository.find(
        str(uuid4()),
        str(uuid4()),
    ) is None


def test_remove_unknown_favorite_is_idempotent(
    favorite_repository: FotosMediaFavoriteRepository,
) -> None:
    """Remover um favorito inexistente não altera registros."""

    assert favorite_repository.remove(
        str(uuid4()),
        str(uuid4()),
    ) is False


def test_list_unknown_user_is_empty(
    favorite_repository: FotosMediaFavoriteRepository,
) -> None:
    """Um usuário sem favoritos recebe uma lista vazia."""

    items, total = favorite_repository.list(
        str(uuid4()),
        page=1,
        page_size=30,
    )

    assert items == []
    assert total == 0


def test_favorite_repository_exposes_expected_operations() -> None:
    """Confirma a interface necessária para a camada de serviço."""

    expected_methods = {
        "exists",
        "find",
        "add",
        "remove",
        "list",
    }

    for method_name in expected_methods:
        assert callable(
            getattr(
                FotosMediaFavoriteRepository,
                method_name,
                None,
            )
        )


def test_favorite_model_relationship_columns() -> None:
    """Confirma os campos utilizados nos relacionamentos."""

    table = FotosMediaFavoriteModel.__table__

    assert table.c.user_id.nullable is False
    assert table.c.media_id.nullable is False

    assert table.c.user_id.primary_key is False
    assert table.c.media_id.primary_key is False

    assert table.c.id.primary_key is True


def test_favorite_repository_returns_no_media_for_unknown_user(
    favorite_repository: FotosMediaFavoriteRepository,
) -> None:
    """Não retorna mídias quando o usuário não possui vínculos."""

    items, total = favorite_repository.list(
        str(uuid4()),
        page=2,
        page_size=30,
    )

    assert total == 0
    assert not items


def test_favorite_repository_uses_media_model() -> None:
    """Confirma que a listagem utiliza o modelo de mídias existente."""

    assert FotosMediaModel.__tablename__ == "fotos_media"

@pytest.fixture()
def favorite_media_context(
    client,
    test_settings,
    test_session_factory,
):
    """Cria usuários e uma fotografia real no banco de testes."""

    from tests.authentication.test_authentication_api import (
        create_environment,
        create_organization,
        create_tenant,
        create_user,
    )
    from tests.authentication.test_user_authorization_api import (
        authorization_headers,
    )
    from tests.fotos.media.test_media_api import upload_image
    from tests.module_management.test_authenticated_modules_api import (
        configure_organization_modules,
    )

    organization = create_organization(client)
    organization_id = str(organization["id"])

    configure_organization_modules(
        client,
        organization_id,
        {"fotos"},
    )

    tenant = create_tenant(client, organization_id)
    environment = create_environment(client, str(tenant["id"]))

    user1 = create_user(
        client,
        organization_id,
        email="favorito1@deja.com",
        module_access={"fotos": "viewer"},
    )

    user2 = create_user(
        client,
        organization_id,
        email="favorito2@deja.com",
        module_access={"fotos": "viewer"},
    )

    administrator = create_user(
        client,
        None,
        email="admin.favoritos@deja.com",
        role="platform_admin",
    )

    headers = authorization_headers(
        test_settings,
        administrator,
    )

    response = upload_image(
        client,
        environment_id=str(environment["id"]),
        album_id=None,
        headers=headers,
    )

    assert response.status_code == 201

    return {
        "user1": str(user1["id"]),
        "user2": str(user2["id"]),
        "media_id": str(response.json()["id"]),
        "session_factory": test_session_factory,
    }


def test_favorite_repository_persists_real_media(
    favorite_media_context,
) -> None:
    """Adiciona e consulta um favorito persistido."""

    context = favorite_media_context

    with context["session_factory"]() as session:
        repository = FotosMediaFavoriteRepository(session)

        favorite = FotosMediaFavoriteModel(
            id=str(uuid4()),
            user_id=context["user1"],
            media_id=context["media_id"],
        )

        saved = repository.add(favorite)

        assert saved.id == favorite.id
        assert repository.exists(
            context["user1"],
            context["media_id"],
        )

        assert repository.find(
            context["user1"],
            context["media_id"],
        ) is not None


def test_favorite_repository_prevents_duplicates(
    favorite_media_context,
) -> None:
    """Adicionar duas vezes não cria favoritos duplicados."""

    context = favorite_media_context

    with context["session_factory"]() as session:
        repository = FotosMediaFavoriteRepository(session)

        first = repository.add(
            FotosMediaFavoriteModel(
                id=str(uuid4()),
                user_id=context["user1"],
                media_id=context["media_id"],
            )
        )

        second = repository.add(
            FotosMediaFavoriteModel(
                id=str(uuid4()),
                user_id=context["user1"],
                media_id=context["media_id"],
            )
        )

        assert first.id == second.id

        items, total = repository.list(context["user1"])

        assert total == 1
        assert len(items) == 1


def test_favorite_repository_isolates_users(
    favorite_media_context,
) -> None:
    """Favoritos de um usuário não aparecem para outro."""

    context = favorite_media_context

    with context["session_factory"]() as session:
        repository = FotosMediaFavoriteRepository(session)

        repository.add(
            FotosMediaFavoriteModel(
                id=str(uuid4()),
                user_id=context["user1"],
                media_id=context["media_id"],
            )
        )

        assert repository.exists(
            context["user1"],
            context["media_id"],
        )

        assert not repository.exists(
            context["user2"],
            context["media_id"],
        )

        items, total = repository.list(context["user2"])

        assert items == []
        assert total == 0


def test_favorite_repository_removes_only_owner_favorite(
    favorite_media_context,
) -> None:
    """A remoção respeita o usuário proprietário."""

    context = favorite_media_context

    with context["session_factory"]() as session:
        repository = FotosMediaFavoriteRepository(session)

        repository.add(
            FotosMediaFavoriteModel(
                id=str(uuid4()),
                user_id=context["user1"],
                media_id=context["media_id"],
            )
        )

        assert repository.remove(
            context["user2"],
            context["media_id"],
        ) is False

        assert repository.exists(
            context["user1"],
            context["media_id"],
        )

        assert repository.remove(
            context["user1"],
            context["media_id"],
        ) is True

        assert not repository.exists(
            context["user1"],
            context["media_id"],
        )


def test_favorite_repository_lists_first_page(
    favorite_media_context,
) -> None:
    """A listagem respeita o limite de paginação."""

    context = favorite_media_context

    with context["session_factory"]() as session:
        repository = FotosMediaFavoriteRepository(session)

        repository.add(
            FotosMediaFavoriteModel(
                id=str(uuid4()),
                user_id=context["user1"],
                media_id=context["media_id"],
            )
        )

        first_page, total = repository.list(
            context["user1"],
            page=1,
            page_size=1,
        )

        second_page, second_total = repository.list(
            context["user1"],
            page=2,
            page_size=1,
        )

        assert total == 1
        assert second_total == 1
        assert len(first_page) == 1
        assert second_page == []

def test_favorite_repository_orders_by_latest_favorite(
    favorite_media_context,
    client,
    test_settings,
) -> None:
    """Lista primeiro a mídia marcada como favorita mais recentemente."""

    from datetime import datetime

    from tests.authentication.test_authentication_api import create_user
    from tests.authentication.test_user_authorization_api import (
        authorization_headers,
    )
    from tests.fotos.media.test_media_api import (
        create_test_jpeg,
        upload_image,
    )

    context = favorite_media_context

    with context["session_factory"]() as session:
        first_media = session.get(
            FotosMediaModel,
            context["media_id"],
        )

        environment_id = first_media.environment_id

    administrator = create_user(
        client,
        None,
        email="admin.ordenacao.favoritos@deja.com",
        role="platform_admin",
    )

    headers = authorization_headers(
        test_settings,
        administrator,
    )

    response = upload_image(
        client,
        environment_id=environment_id,
        album_id=None,
        headers=headers,
        file_name="segunda-foto.jpg",
        content=create_test_jpeg(width=20, height=14),
    )

    assert response.status_code == 201

    second_media_id = str(response.json()["id"])

    with context["session_factory"]() as session:
        repository = FotosMediaFavoriteRepository(session)

        older = FotosMediaFavoriteModel(
            id=str(uuid4()),
            user_id=context["user1"],
            media_id=context["media_id"],
            created_at=datetime(2026, 10, 10, 10, 0),
        )

        newer = FotosMediaFavoriteModel(
            id=str(uuid4()),
            user_id=context["user1"],
            media_id=second_media_id,
            created_at=datetime(2026, 10, 11, 10, 0),
        )

        repository.add(older)
        repository.add(newer)

        items, total = repository.list(
            context["user1"],
            page=1,
            page_size=30,
        )

        assert total == 2
        assert [item.id for item in items] == [
            second_media_id,
            context["media_id"],
        ]

def test_favorite_repository_filters_institutional_scope(
    favorite_media_context,
) -> None:
    """Aplica filtros institucionais antes da contagem e paginação."""

    context = favorite_media_context

    with context["session_factory"]() as session:
        repository = FotosMediaFavoriteRepository(session)

        media = session.get(
            FotosMediaModel,
            context["media_id"],
        )

        assert media is not None

        repository.add(
            FotosMediaFavoriteModel(
                id=str(uuid4()),
                user_id=context["user1"],
                media_id=context["media_id"],
            )
        )

        items, total = repository.list(
            context["user1"],
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            page=1,
            page_size=30,
        )

        assert total == 1
        assert len(items) == 1
        assert items[0].id == media.id

        items, total = repository.list(
            context["user1"],
            organization_id=str(uuid4()),
            page=1,
            page_size=30,
        )

        assert items == []
        assert total == 0

        items, total = repository.list(
            context["user1"],
            tenant_id=str(uuid4()),
            page=1,
            page_size=30,
        )

        assert items == []
        assert total == 0

        items, total = repository.list(
            context["user1"],
            environment_id=str(uuid4()),
            page=1,
            page_size=30,
        )

        assert items == []
        assert total == 0