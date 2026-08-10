from uuid import uuid4

from fastapi.testclient import TestClient

COMPANIES_URL = "/api/companies"
INDICATORS_URL = "/api/indicators"

COMPANY = {
    "legal_name": "Deja Tecnologia Ltda",
    "trade_name": "Deja Tecnologia",
    "document": "12.345.678/0001-90",
    "email": "contato@deja.com.br",
    "phone": "(54) 99999-0000",
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


def create_company(
    client: TestClient,
    payload: dict[str, str] = COMPANY,
) -> dict[str, object]:
    """Cadastra uma empresa e retorna o corpo da resposta."""

    response = client.post(COMPANIES_URL, json=payload)

    assert response.status_code == 201
    return response.json()


def indicator_payload(
    company_id: str,
    **overrides: object,
) -> dict[str, object]:
    """Cria os dados válidos de um indicador."""

    payload: dict[str, object] = {
        "company_id": company_id,
        "name": "Margem líquida",
        "description": "Percentual de lucro líquido sobre a receita.",
        "unit": "%",
        "direction": "higher_is_better",
        "target_value": "15.5000",
        "status": "active",
    }
    payload.update(overrides)
    return payload


def create_indicator(
    client: TestClient,
    company_id: str,
    **overrides: object,
) -> dict[str, object]:
    """Cadastra um indicador e retorna o corpo da resposta."""

    response = client.post(
        INDICATORS_URL,
        json=indicator_payload(company_id, **overrides),
    )

    assert response.status_code == 201
    return response.json()


def test_create_indicator_normalizes_and_returns_data(
    client: TestClient,
) -> None:
    """Cadastra um indicador normalizando os textos informados."""

    company = create_company(client)

    response = client.post(
        INDICATORS_URL,
        json=indicator_payload(
            str(company["id"]),
            name="  Margem líquida  ",
            description="  Percentual de lucro líquido.  ",
            unit="  %  ",
        ),
    )

    assert response.status_code == 201

    body = response.json()

    assert len(body["id"]) == 36
    assert body["company_id"] == company["id"]
    assert body["name"] == "Margem líquida"
    assert body["description"] == "Percentual de lucro líquido."
    assert body["unit"] == "%"
    assert body["direction"] == "higher_is_better"
    assert body["target_value"] == "15.5000"
    assert body["status"] == "active"
    assert body["created_at"]
    assert body["updated_at"]


def test_create_indicator_converts_blank_description_to_none(
    client: TestClient,
) -> None:
    """Converte uma descrição composta por espaços em valor nulo."""

    company = create_company(client)
    indicator = create_indicator(
        client,
        str(company["id"]),
        description="   ",
    )

    assert indicator["description"] is None


def test_list_indicators_returns_name_order(
    client: TestClient,
) -> None:
    """Lista os indicadores ordenados pelo nome."""

    company = create_company(client)

    create_indicator(
        client,
        str(company["id"]),
        name="Receita líquida",
        unit="R$",
        target_value="100000.0000",
    )
    create_indicator(
        client,
        str(company["id"]),
        name="Margem líquida",
    )

    response = client.get(INDICATORS_URL)

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert [indicator["name"] for indicator in body] == [
        "Margem líquida",
        "Receita líquida",
    ]


def test_list_indicators_filters_by_company(
    client: TestClient,
) -> None:
    """Lista somente os indicadores pertencentes à empresa informada."""

    first_company = create_company(client)
    second_company = create_company(client, SECOND_COMPANY)

    first_indicator = create_indicator(
        client,
        str(first_company["id"]),
    )
    create_indicator(
        client,
        str(second_company["id"]),
        name="Custo operacional",
        unit="R$",
        direction="lower_is_better",
        target_value="50000.0000",
    )

    response = client.get(
        INDICATORS_URL,
        params={"company_id": first_company["id"]},
    )

    assert response.status_code == 200
    assert response.json() == [first_indicator]


def test_get_indicator_by_id(client: TestClient) -> None:
    """Consulta um indicador pelo identificador."""

    company = create_company(client)
    indicator = create_indicator(client, str(company["id"]))

    response = client.get(f"{INDICATORS_URL}/{indicator['id']}")

    assert response.status_code == 200
    assert response.json() == indicator


def test_update_indicator(client: TestClient) -> None:
    """Atualiza integralmente um indicador existente."""

    company = create_company(client)
    indicator = create_indicator(client, str(company["id"]))

    response = client.put(
        f"{INDICATORS_URL}/{indicator['id']}",
        json=indicator_payload(
            str(company["id"]),
            name="Margem operacional",
            description="Resultado operacional sobre a receita.",
            direction="lower_is_better",
            target_value="12.2500",
            status="inactive",
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == indicator["id"]
    assert body["company_id"] == company["id"]
    assert body["name"] == "Margem operacional"
    assert body["description"] == (
        "Resultado operacional sobre a receita."
    )
    assert body["direction"] == "lower_is_better"
    assert body["target_value"] == "12.2500"
    assert body["status"] == "inactive"


def test_update_indicator_can_move_to_another_company(
    client: TestClient,
) -> None:
    """Permite transferir um indicador para outra empresa existente."""

    first_company = create_company(client)
    second_company = create_company(client, SECOND_COMPANY)
    indicator = create_indicator(client, str(first_company["id"]))

    response = client.put(
        f"{INDICATORS_URL}/{indicator['id']}",
        json=indicator_payload(str(second_company["id"])),
    )

    assert response.status_code == 200
    assert response.json()["company_id"] == second_company["id"]


def test_delete_indicator(client: TestClient) -> None:
    """Exclui um indicador e impede consultas posteriores."""

    company = create_company(client)
    indicator = create_indicator(client, str(company["id"]))

    delete_response = client.delete(
        f"{INDICATORS_URL}/{indicator['id']}",
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(
        f"{INDICATORS_URL}/{indicator['id']}",
    )

    assert get_response.status_code == 404
    assert get_response.json()["error"] == "indicator_not_found"


def test_create_indicator_rejects_duplicate_name_in_same_company(
    client: TestClient,
) -> None:
    """Rejeita nome de indicador repetido dentro da mesma empresa."""

    company = create_company(client)
    create_indicator(client, str(company["id"]))

    response = client.post(
        INDICATORS_URL,
        json=indicator_payload(str(company["id"])),
    )

    assert response.status_code == 409
    assert response.json()["error"] == "indicator_name_already_exists"


def test_same_indicator_name_is_allowed_for_different_companies(
    client: TestClient,
) -> None:
    """Permite o mesmo nome de indicador em empresas diferentes."""

    first_company = create_company(client)
    second_company = create_company(client, SECOND_COMPANY)

    create_indicator(client, str(first_company["id"]))

    response = client.post(
        INDICATORS_URL,
        json=indicator_payload(str(second_company["id"])),
    )

    assert response.status_code == 201


def test_update_indicator_keeps_its_own_name(
    client: TestClient,
) -> None:
    """Permite atualizar o indicador mantendo o próprio nome."""

    company = create_company(client)
    indicator = create_indicator(client, str(company["id"]))

    response = client.put(
        f"{INDICATORS_URL}/{indicator['id']}",
        json=indicator_payload(str(company["id"])),
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Margem líquida"


def test_create_indicator_rejects_unknown_company(
    client: TestClient,
) -> None:
    """Rejeita o cadastro para uma empresa inexistente."""

    response = client.post(
        INDICATORS_URL,
        json=indicator_payload(str(uuid4())),
    )

    assert response.status_code == 404
    assert response.json()["error"] == "company_not_found"


def test_filter_rejects_unknown_company(client: TestClient) -> None:
    """Rejeita o filtro por uma empresa inexistente."""

    response = client.get(
        INDICATORS_URL,
        params={"company_id": str(uuid4())},
    )

    assert response.status_code == 404
    assert response.json()["error"] == "company_not_found"


def test_update_indicator_rejects_unknown_company(
    client: TestClient,
) -> None:
    """Rejeita a transferência para uma empresa inexistente."""

    company = create_company(client)
    indicator = create_indicator(client, str(company["id"]))

    response = client.put(
        f"{INDICATORS_URL}/{indicator['id']}",
        json=indicator_payload(str(uuid4())),
    )

    assert response.status_code == 404
    assert response.json()["error"] == "company_not_found"


def test_get_unknown_indicator_returns_not_found(
    client: TestClient,
) -> None:
    """Retorna 404 ao consultar um indicador inexistente."""

    response = client.get(f"{INDICATORS_URL}/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"] == "indicator_not_found"


def test_update_unknown_indicator_returns_not_found(
    client: TestClient,
) -> None:
    """Retorna 404 ao atualizar um indicador inexistente."""

    company = create_company(client)

    response = client.put(
        f"{INDICATORS_URL}/{uuid4()}",
        json=indicator_payload(str(company["id"])),
    )

    assert response.status_code == 404
    assert response.json()["error"] == "indicator_not_found"


def test_delete_unknown_indicator_returns_not_found(
    client: TestClient,
) -> None:
    """Retorna 404 ao excluir um indicador inexistente."""

    response = client.delete(f"{INDICATORS_URL}/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"] == "indicator_not_found"


def test_create_indicator_rejects_invalid_direction(
    client: TestClient,
) -> None:
    """Rejeita uma direção de avaliação inválida."""

    company = create_company(client)

    response = client.post(
        INDICATORS_URL,
        json=indicator_payload(
            str(company["id"]),
            direction="invalid",
        ),
    )

    assert response.status_code == 422


def test_create_indicator_rejects_invalid_status(
    client: TestClient,
) -> None:
    """Rejeita um estado de indicador inválido."""

    company = create_company(client)

    response = client.post(
        INDICATORS_URL,
        json=indicator_payload(
            str(company["id"]),
            status="invalid",
        ),
    )

    assert response.status_code == 422


def test_indicator_id_requires_36_characters(
    client: TestClient,
) -> None:
    """Rejeita identificador que não possui 36 caracteres."""

    response = client.get(f"{INDICATORS_URL}/invalid-id")

    assert response.status_code == 422


def test_company_filter_requires_36_characters(
    client: TestClient,
) -> None:
    """Rejeita filtro de empresa que não possui 36 caracteres."""

    response = client.get(
        INDICATORS_URL,
        params={"company_id": "invalid-id"},
    )

    assert response.status_code == 422