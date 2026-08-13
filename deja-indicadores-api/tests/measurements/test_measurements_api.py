from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from tests.indicators.test_indicators_api import (
    create_company as insert_test_company,
)


def company_payload(
    *,
    name: str = "Empresa de Teste",
    document: str = "12.345.678/0001-90",
) -> dict[str, object]:
    """Monta um payload válido de empresa."""

    return {
        "legal_name": f"{name} Ltda",
        "trade_name": name,
        "document": document,
        "email": "contato@empresa.com.br",
        "phone": "(54) 99999-9999",
        "status": "active",
    }


def indicator_payload(
    company_id: str,
    *,
    name: str = "Faturamento",
) -> dict[str, object]:
    """Monta um payload válido de indicador."""

    return {
        "company_id": company_id,
        "name": name,
        "description": "Faturamento mensal da empresa.",
        "unit": "BRL",
        "direction": "higher_is_better",
        "target_value": "100000.0000",
        "status": "active",
    }


def measurement_payload(
    indicator_id: str,
    *,
    reference_date: str = "2026-08-01",
    actual_value: str = "87500.2500",
    observation: str | None = "Valor consolidado do período.",
) -> dict[str, object]:
    """Monta um payload válido de medição."""

    return {
        "indicator_id": indicator_id,
        "reference_date": reference_date,
        "actual_value": actual_value,
        "observation": observation,
    }


def create_company(
    client: TestClient,
    *,
    name: str = "Empresa de Teste",
    document: str = "12345678000190",
) -> dict[str, object]:
    """Insere e retorna uma empresa válida para os testes."""

    payload = company_payload(
        name=name,
        document=document,
    )

    return insert_test_company(
        client,
        {field_name: str(value) for field_name, value in payload.items()},
    )


def create_indicator(
    client: TestClient,
    company_id: str,
    *,
    name: str = "Faturamento",
) -> dict[str, object]:
    """Cadastra e retorna um indicador válido."""

    response = client.post(
        "/api/indicators",
        json=indicator_payload(company_id, name=name),
    )

    assert response.status_code == 201
    return response.json()


def create_measurement(
    client: TestClient,
    indicator_id: str,
    *,
    reference_date: str = "2026-08-01",
    actual_value: str = "87500.2500",
    observation: str | None = "Valor consolidado do período.",
) -> dict[str, object]:
    """Cadastra e retorna uma medição válida."""

    response = client.post(
        "/api/measurements",
        json=measurement_payload(
            indicator_id,
            reference_date=reference_date,
            actual_value=actual_value,
            observation=observation,
        ),
    )

    assert response.status_code == 201
    return response.json()


def test_create_measurement(client: TestClient) -> None:
    """Deve cadastrar uma medição vinculada a um indicador existente."""

    company = create_company(client)
    indicator = create_indicator(client, company["id"])

    response = client.post(
        "/api/measurements",
        json=measurement_payload(
            indicator["id"],
            observation="  Fechamento validado.  ",
        ),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["indicator_id"] == indicator["id"]
    assert body["reference_date"] == "2026-08-01"
    assert Decimal(body["actual_value"]) == Decimal("87500.2500")
    assert body["observation"] == "Fechamento validado."
    assert body["created_by"] is None
    assert body["id"]
    assert body["created_at"]
    assert body["updated_at"]


def test_create_measurement_normalizes_empty_observation(
    client: TestClient,
) -> None:
    """Deve converter uma observação vazia em valor nulo."""

    company = create_company(client)
    indicator = create_indicator(client, company["id"])

    response = client.post(
        "/api/measurements",
        json=measurement_payload(
            indicator["id"],
            observation="   ",
        ),
    )

    assert response.status_code == 201
    assert response.json()["observation"] is None


def test_create_measurement_for_missing_indicator(
    client: TestClient,
) -> None:
    """Deve rejeitar cadastro para um indicador inexistente."""

    missing_indicator_id = str(uuid4())

    response = client.post(
        "/api/measurements",
        json=measurement_payload(missing_indicator_id),
    )

    assert response.status_code == 404
    assert response.json()["error"] == "indicator_not_found"


def test_create_duplicate_measurement(client: TestClient) -> None:
    """Deve impedir duas medições do mesmo indicador na mesma data."""

    company = create_company(client)
    indicator = create_indicator(client, company["id"])

    create_measurement(client, indicator["id"])

    response = client.post(
        "/api/measurements",
        json=measurement_payload(
            indicator["id"],
            actual_value="90000.0000",
        ),
    )

    assert response.status_code == 409
    assert response.json()["error"] == "measurement_already_exists"


def test_list_measurements_ordered_by_reference_date(
    client: TestClient,
) -> None:
    """Deve listar as medições em ordem crescente de data."""

    company = create_company(client)
    indicator = create_indicator(client, company["id"])

    create_measurement(
        client,
        indicator["id"],
        reference_date="2026-08-10",
    )
    create_measurement(
        client,
        indicator["id"],
        reference_date="2026-06-10",
    )
    create_measurement(
        client,
        indicator["id"],
        reference_date="2026-07-10",
    )

    response = client.get("/api/measurements")

    assert response.status_code == 200
    assert [item["reference_date"] for item in response.json()] == [
        "2026-06-10",
        "2026-07-10",
        "2026-08-10",
    ]


def test_list_measurements_filtered_by_company(
    client: TestClient,
) -> None:
    """Deve filtrar medições pela empresa proprietária dos indicadores."""

    first_company = create_company(client)
    second_company = create_company(
        client,
        name="Segunda Empresa",
        document="98.765.432/0001-10",
    )
    first_indicator = create_indicator(
        client,
        first_company["id"],
        name="Faturamento",
    )
    second_indicator = create_indicator(
        client,
        second_company["id"],
        name="Produtividade",
    )

    create_measurement(client, first_indicator["id"])
    create_measurement(client, second_indicator["id"])

    response = client.get(
        "/api/measurements",
        params={"company_id": first_company["id"]},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["indicator_id"] == first_indicator["id"]


def test_list_measurements_filtered_by_indicator(
    client: TestClient,
) -> None:
    """Deve filtrar medições pelo indicador informado."""

    company = create_company(client)
    first_indicator = create_indicator(
        client,
        company["id"],
        name="Faturamento",
    )
    second_indicator = create_indicator(
        client,
        company["id"],
        name="Produtividade",
    )

    create_measurement(client, first_indicator["id"])
    create_measurement(client, second_indicator["id"])

    response = client.get(
        "/api/measurements",
        params={"indicator_id": second_indicator["id"]},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["indicator_id"] == second_indicator["id"]


def test_list_measurements_filtered_by_inclusive_period(
    client: TestClient,
) -> None:
    """Deve aplicar filtros inclusivos de data inicial e final."""

    company = create_company(client)
    indicator = create_indicator(client, company["id"])

    create_measurement(
        client,
        indicator["id"],
        reference_date="2026-06-30",
    )
    create_measurement(
        client,
        indicator["id"],
        reference_date="2026-07-01",
    )
    create_measurement(
        client,
        indicator["id"],
        reference_date="2026-07-31",
    )
    create_measurement(
        client,
        indicator["id"],
        reference_date="2026-08-01",
    )

    response = client.get(
        "/api/measurements",
        params={
            "start_date": "2026-07-01",
            "end_date": "2026-07-31",
        },
    )

    assert response.status_code == 200
    assert [item["reference_date"] for item in response.json()] == [
        "2026-07-01",
        "2026-07-31",
    ]


def test_list_measurements_for_missing_company(
    client: TestClient,
) -> None:
    """Deve rejeitar o filtro por uma empresa inexistente."""

    response = client.get(
        "/api/measurements",
        params={"company_id": str(uuid4())},
    )

    assert response.status_code == 404
    assert response.json()["error"] == "company_not_found"


def test_list_measurements_for_missing_indicator(
    client: TestClient,
) -> None:
    """Deve rejeitar o filtro por um indicador inexistente."""

    response = client.get(
        "/api/measurements",
        params={"indicator_id": str(uuid4())},
    )

    assert response.status_code == 404
    assert response.json()["error"] == "indicator_not_found"


def test_list_measurements_with_unrelated_company_and_indicator(
    client: TestClient,
) -> None:
    """Deve retornar lista vazia quando os filtros não possuem vínculo."""

    first_company = create_company(client)
    second_company = create_company(
        client,
        name="Segunda Empresa",
        document="98.765.432/0001-10",
    )
    indicator = create_indicator(client, first_company["id"])

    create_measurement(client, indicator["id"])

    response = client.get(
        "/api/measurements",
        params={
            "company_id": second_company["id"],
            "indicator_id": indicator["id"],
        },
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_measurement(client: TestClient) -> None:
    """Deve consultar uma medição existente pelo identificador."""

    company = create_company(client)
    indicator = create_indicator(client, company["id"])
    measurement = create_measurement(client, indicator["id"])

    response = client.get(f"/api/measurements/{measurement['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == measurement["id"]


def test_get_missing_measurement(client: TestClient) -> None:
    """Deve retornar recurso não encontrado para uma medição inexistente."""

    response = client.get(f"/api/measurements/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"] == "measurement_not_found"


def test_update_measurement(client: TestClient) -> None:
    """Deve atualizar integralmente uma medição existente."""

    company = create_company(client)
    first_indicator = create_indicator(
        client,
        company["id"],
        name="Faturamento",
    )
    second_indicator = create_indicator(
        client,
        company["id"],
        name="Margem",
    )
    measurement = create_measurement(client, first_indicator["id"])

    response = client.put(
        f"/api/measurements/{measurement['id']}",
        json=measurement_payload(
            second_indicator["id"],
            reference_date="2026-08-02",
            actual_value="92500.7500",
            observation="  Valor revisado.  ",
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == measurement["id"]
    assert body["indicator_id"] == second_indicator["id"]
    assert body["reference_date"] == "2026-08-02"
    assert Decimal(body["actual_value"]) == Decimal("92500.7500")
    assert body["observation"] == "Valor revisado."


def test_update_missing_measurement(client: TestClient) -> None:
    """Deve rejeitar atualização de uma medição inexistente."""

    company = create_company(client)
    indicator = create_indicator(client, company["id"])

    response = client.put(
        f"/api/measurements/{uuid4()}",
        json=measurement_payload(indicator["id"]),
    )

    assert response.status_code == 404
    assert response.json()["error"] == "measurement_not_found"


def test_update_measurement_for_missing_indicator(
    client: TestClient,
) -> None:
    """Deve rejeitar atualização para um indicador inexistente."""

    company = create_company(client)
    indicator = create_indicator(client, company["id"])
    measurement = create_measurement(client, indicator["id"])

    response = client.put(
        f"/api/measurements/{measurement['id']}",
        json=measurement_payload(str(uuid4())),
    )

    assert response.status_code == 404
    assert response.json()["error"] == "indicator_not_found"


def test_update_measurement_to_duplicate_period(
    client: TestClient,
) -> None:
    """Deve impedir atualização que produza uma medição duplicada."""

    company = create_company(client)
    indicator = create_indicator(client, company["id"])

    first_measurement = create_measurement(
        client,
        indicator["id"],
        reference_date="2026-08-01",
    )
    create_measurement(
        client,
        indicator["id"],
        reference_date="2026-08-02",
    )

    response = client.put(
        f"/api/measurements/{first_measurement['id']}",
        json=measurement_payload(
            indicator["id"],
            reference_date="2026-08-02",
        ),
    )

    assert response.status_code == 409
    assert response.json()["error"] == "measurement_already_exists"


def test_delete_measurement(client: TestClient) -> None:
    """Deve excluir uma medição existente."""

    company = create_company(client)
    indicator = create_indicator(client, company["id"])
    measurement = create_measurement(client, indicator["id"])

    delete_response = client.delete(f"/api/measurements/{measurement['id']}")
    get_response = client.get(f"/api/measurements/{measurement['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_delete_missing_measurement(client: TestClient) -> None:
    """Deve retornar recurso não encontrado ao excluir medição inexistente."""

    response = client.delete(f"/api/measurements/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"] == "measurement_not_found"


def test_delete_indicator_with_measurements(client: TestClient) -> None:
    """Deve impedir a exclusão de indicador que possua medições."""

    company = create_company(client)
    indicator = create_indicator(client, company["id"])
    create_measurement(client, indicator["id"])

    response = client.delete(f"/api/indicators/{indicator['id']}")

    assert response.status_code == 409
    assert response.json()["error"] == "indicator_has_measurements"
