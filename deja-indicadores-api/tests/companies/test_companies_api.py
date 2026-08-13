from collections.abc import Mapping
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from tests.authentication.test_authentication_api import (
    create_environment,
    create_organization,
    create_tenant,
    create_user,
)
from tests.authentication.test_user_authorization_api import (
    authorization_headers,
)

COMPANIES_URL = "/api/companies"
INDICATORS_URL = "/api/indicators"

FIRST_COMPANY = {
    "legal_name": "Deja Tecnologia Ltda",
    "trade_name": "Deja Tecnologia",
    "document": "12.345.678/0001-90",
    "email": "CONTATO@DEJA.COM.BR",
    "phone": " (54) 99999-0000 ",
    "status": "active",
}

SECOND_COMPANY = {
    "legal_name": "Empresa Exemplo Ltda",
    "trade_name": "Empresa Exemplo",
    "document": "98.765.432/0001-10",
    "email": "contato@exemplo.com.br",
    "phone": "(54) 98888-0000",
    "status": "active",
}


@pytest.fixture()
def company_context(
    client: TestClient,
    test_settings: Settings,
) -> tuple[str, Mapping[str, str]]:
    """Cria ambiente e identidade global para os testes de empresas."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    environment = create_environment(client, str(tenant["id"]))
    administrator = create_user(
        client,
        None,
        email="platform.admin.companies@deja.com",
        role="platform_admin",
    )

    return (
        str(environment["id"]),
        authorization_headers(test_settings, administrator),
    )


def company_payload(
    payload: dict[str, str],
    environment_id: str,
) -> dict[str, str]:
    """Adiciona o ambiente institucional ao contrato da empresa."""

    return {
        "environment_id": environment_id,
        **payload,
    }


def create_company(
    client: TestClient,
    payload: dict[str, str],
    environment_id: str,
    headers: Mapping[str, str],
) -> dict[str, object]:
    """Cadastra uma empresa e retorna o corpo da resposta."""

    response = client.post(
        COMPANIES_URL,
        json=company_payload(payload, environment_id),
        headers=headers,
    )

    assert response.status_code == 201
    return response.json()


def create_indicator(
    client: TestClient,
    company_id: str,
) -> dict[str, object]:
    """Cadastra um indicador para a empresa informada."""

    response = client.post(
        INDICATORS_URL,
        json={
            "company_id": company_id,
            "name": "Margem líquida",
            "description": "Percentual de lucro líquido sobre a receita.",
            "unit": "%",
            "direction": "higher_is_better",
            "target_value": "15.5000",
            "status": "active",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_company_normalizes_and_returns_data(
    client: TestClient,
    company_context: tuple[str, Mapping[str, str]],
) -> None:
    """Cadastra uma empresa normalizando os campos informados."""

    environment_id, headers = company_context
    payload = {
        **FIRST_COMPANY,
        "legal_name": "  Deja Tecnologia Ltda  ",
        "trade_name": "  Deja Tecnologia  ",
    }

    response = client.post(
        COMPANIES_URL,
        json=company_payload(payload, environment_id),
        headers=headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert len(body["id"]) == 36
    assert body["environment_id"] == environment_id
    assert body["legal_name"] == "Deja Tecnologia Ltda"
    assert body["trade_name"] == "Deja Tecnologia"
    assert body["document"] == "12345678000190"
    assert body["email"] == "contato@deja.com.br"
    assert body["phone"] == "(54) 99999-0000"
    assert body["status"] == "active"
    assert body["created_at"]
    assert body["updated_at"]


def test_list_companies_returns_trade_name_order(
    client: TestClient,
    company_context: tuple[str, Mapping[str, str]],
) -> None:
    """Lista as empresas ordenadas pelo nome fantasia."""

    environment_id, headers = company_context
    create_company(
        client,
        FIRST_COMPANY,
        environment_id,
        headers,
    )
    create_company(
        client,
        SECOND_COMPANY,
        environment_id,
        headers,
    )

    response = client.get(
        COMPANIES_URL,
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert [company["trade_name"] for company in body] == [
        "Deja Tecnologia",
        "Empresa Exemplo",
    ]


def test_get_company_by_id(
    client: TestClient,
    company_context: tuple[str, Mapping[str, str]],
) -> None:
    """Consulta uma empresa pelo identificador."""

    environment_id, headers = company_context
    company = create_company(
        client,
        FIRST_COMPANY,
        environment_id,
        headers,
    )

    response = client.get(
        f"{COMPANIES_URL}/{company['id']}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == company


def test_update_company(
    client: TestClient,
    company_context: tuple[str, Mapping[str, str]],
) -> None:
    """Atualiza integralmente uma empresa existente."""

    environment_id, headers = company_context
    company = create_company(
        client,
        FIRST_COMPANY,
        environment_id,
        headers,
    )
    update_payload = {
        **FIRST_COMPANY,
        "legal_name": "Deja Sistemas Ltda",
        "trade_name": "Deja Sistemas",
        "email": "sistemas@deja.com.br",
        "status": "inactive",
    }

    response = client.put(
        f"{COMPANIES_URL}/{company['id']}",
        json=company_payload(update_payload, environment_id),
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == company["id"]
    assert body["environment_id"] == environment_id
    assert body["legal_name"] == "Deja Sistemas Ltda"
    assert body["trade_name"] == "Deja Sistemas"
    assert body["email"] == "sistemas@deja.com.br"
    assert body["status"] == "inactive"
    assert body["document"] == "12345678000190"


def test_update_company_keeps_its_own_document(
    client: TestClient,
    company_context: tuple[str, Mapping[str, str]],
) -> None:
    """Permite atualizar a empresa mantendo o próprio documento."""

    environment_id, headers = company_context
    company = create_company(
        client,
        FIRST_COMPANY,
        environment_id,
        headers,
    )

    response = client.put(
        f"{COMPANIES_URL}/{company['id']}",
        json=company_payload(FIRST_COMPANY, environment_id),
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["document"] == "12345678000190"


def test_delete_company(
    client: TestClient,
    company_context: tuple[str, Mapping[str, str]],
) -> None:
    """Exclui uma empresa e impede consultas posteriores."""

    environment_id, headers = company_context
    company = create_company(
        client,
        FIRST_COMPANY,
        environment_id,
        headers,
    )

    delete_response = client.delete(
        f"{COMPANIES_URL}/{company['id']}",
        headers=headers,
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(
        f"{COMPANIES_URL}/{company['id']}",
        headers=headers,
    )

    assert get_response.status_code == 404
    assert get_response.json()["error"] == "company_not_found"


def test_delete_company_rejects_when_it_has_indicators(
    client: TestClient,
    company_context: tuple[str, Mapping[str, str]],
) -> None:
    """Impede excluir uma empresa que possua indicadores cadastrados."""

    environment_id, headers = company_context
    company = create_company(
        client,
        FIRST_COMPANY,
        environment_id,
        headers,
    )
    create_indicator(client, str(company["id"]))

    response = client.delete(
        f"{COMPANIES_URL}/{company['id']}",
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["error"] == "company_has_indicators"

    get_response = client.get(
        f"{COMPANIES_URL}/{company['id']}",
        headers=headers,
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == company["id"]


def test_create_company_rejects_duplicate_document(
    client: TestClient,
    company_context: tuple[str, Mapping[str, str]],
) -> None:
    """Rejeita um documento já associado a outra empresa."""

    environment_id, headers = company_context
    create_company(
        client,
        FIRST_COMPANY,
        environment_id,
        headers,
    )

    response = client.post(
        COMPANIES_URL,
        json=company_payload(
            {
                **SECOND_COMPANY,
                "document": FIRST_COMPANY["document"],
            },
            environment_id,
        ),
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["error"] == "company_document_already_exists"


def test_update_company_rejects_another_company_document(
    client: TestClient,
    company_context: tuple[str, Mapping[str, str]],
) -> None:
    """Rejeita documento pertencente a outra empresa."""

    environment_id, headers = company_context
    first_company = create_company(
        client,
        FIRST_COMPANY,
        environment_id,
        headers,
    )
    second_company = create_company(
        client,
        SECOND_COMPANY,
        environment_id,
        headers,
    )

    response = client.put(
        f"{COMPANIES_URL}/{second_company['id']}",
        json=company_payload(
            {
                **SECOND_COMPANY,
                "document": FIRST_COMPANY["document"],
            },
            environment_id,
        ),
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["error"] == "company_document_already_exists"
    assert first_company["document"] == "12345678000190"


def test_get_unknown_company_returns_not_found(
    client: TestClient,
    company_context: tuple[str, Mapping[str, str]],
) -> None:
    """Retorna 404 ao consultar uma empresa inexistente."""

    _, headers = company_context
    company_id = str(uuid4())

    response = client.get(
        f"{COMPANIES_URL}/{company_id}",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["error"] == "company_not_found"


def test_update_unknown_company_returns_not_found(
    client: TestClient,
    company_context: tuple[str, Mapping[str, str]],
) -> None:
    """Retorna 404 ao atualizar uma empresa inexistente."""

    environment_id, headers = company_context
    company_id = str(uuid4())

    response = client.put(
        f"{COMPANIES_URL}/{company_id}",
        json=company_payload(FIRST_COMPANY, environment_id),
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["error"] == "company_not_found"


def test_delete_unknown_company_returns_not_found(
    client: TestClient,
    company_context: tuple[str, Mapping[str, str]],
) -> None:
    """Retorna 404 ao excluir uma empresa inexistente."""

    _, headers = company_context
    company_id = str(uuid4())

    response = client.delete(
        f"{COMPANIES_URL}/{company_id}",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["error"] == "company_not_found"


def test_create_company_rejects_invalid_document(
    client: TestClient,
    company_context: tuple[str, Mapping[str, str]],
) -> None:
    """Rejeita documento que não possui 11 ou 14 números."""

    environment_id, headers = company_context
    response = client.post(
        COMPANIES_URL,
        json=company_payload(
            {
                **FIRST_COMPANY,
                "document": "1234",
            },
            environment_id,
        ),
        headers=headers,
    )

    assert response.status_code == 422


def test_create_company_rejects_invalid_email(
    client: TestClient,
    company_context: tuple[str, Mapping[str, str]],
) -> None:
    """Rejeita endereço de e-mail inválido."""

    environment_id, headers = company_context
    response = client.post(
        COMPANIES_URL,
        json=company_payload(
            {
                **FIRST_COMPANY,
                "email": "email-invalido",
            },
            environment_id,
        ),
        headers=headers,
    )

    assert response.status_code == 422


def test_company_id_requires_36_characters(
    client: TestClient,
    company_context: tuple[str, Mapping[str, str]],
) -> None:
    """Rejeita identificador que não possui 36 caracteres."""

    _, headers = company_context
    response = client.get(
        f"{COMPANIES_URL}/invalid-id",
        headers=headers,
    )

    assert response.status_code == 422
