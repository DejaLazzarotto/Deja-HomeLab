from datetime import datetime

from fastapi.testclient import TestClient

from tests.indicators.test_indicators_api import (
    create_company as insert_test_company,
)


def create_company(client: TestClient) -> dict:
    """Insere uma empresa para os cenários de relatório."""

    return insert_test_company(
        client,
        {
            "legal_name": "Empresa Relatório Ltda",
            "trade_name": "Empresa Relatório",
            "document": "55555555000155",
            "email": None,
            "phone": None,
            "status": "active",
        },
    )


def create_indicator(
    client: TestClient,
    company_id: str,
) -> dict:
    """Cria um indicador para os cenários de relatório."""

    response = client.post(
        "/api/indicators",
        json={
            "company_id": company_id,
            "name": "Faturamento mensal",
            "description": None,
            "unit": "BRL",
            "direction": "higher_is_better",
            "target_value": "10000.0000",
            "status": "active",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_measurement(
    client: TestClient,
    indicator_id: str,
) -> dict:
    """Cria uma medição para os cenários de relatório."""

    response = client.post(
        "/api/measurements",
        json={
            "indicator_id": indicator_id,
            "reference_date": "2026-08-01",
            "actual_value": "12000.0000",
            "observation": "Meta superada",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_get_management_report_without_data(
    client: TestClient,
) -> None:
    """Gera um relatório gerencial vazio com metadados."""

    response = client.get("/api/reports/management")

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Relatório Gerencial de Indicadores"
    assert (
        datetime.fromisoformat(data["generated_at"].replace("Z", "+00:00")).tzinfo
        is not None
    )
    assert data["filters"] == {
        "company_id": None,
        "start_date": None,
        "end_date": None,
    }
    assert data["overview"] == {
        "totals": {
            "companies": 0,
            "indicators": 0,
            "measurements": 0,
        },
        "companies_by_status": [],
        "indicators_by_status": [],
        "indicators": [],
    }


def test_get_management_report_with_filters_and_data(
    client: TestClient,
) -> None:
    """Gera o relatório com filtros e dados gerenciais consolidados."""

    company = create_company(client)
    indicator = create_indicator(client, company["id"])
    measurement = create_measurement(client, indicator["id"])

    response = client.get(
        "/api/reports/management",
        params={
            "company_id": company["id"],
            "start_date": "2026-08-01",
            "end_date": "2026-08-31",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filters"] == {
        "company_id": company["id"],
        "start_date": "2026-08-01",
        "end_date": "2026-08-31",
    }
    assert data["overview"]["totals"] == {
        "companies": 1,
        "indicators": 1,
        "measurements": 1,
    }

    report_indicator = data["overview"]["indicators"][0]

    assert report_indicator["id"] == indicator["id"]
    assert report_indicator["company_id"] == company["id"]
    assert report_indicator["current_measurement"]["id"] == measurement["id"]
    assert report_indicator["achievement_percentage"] == "120.0000"
    assert report_indicator["situation"] == "on_target"


def test_get_management_report_rejects_invalid_period(
    client: TestClient,
) -> None:
    """Rejeita período gerencial com datas incoerentes."""

    response = client.get(
        "/api/reports/management",
        params={
            "start_date": "2026-08-31",
            "end_date": "2026-08-01",
        },
    )

    assert response.status_code == 400
