from decimal import Decimal

from fastapi.testclient import TestClient


def create_company(
    client: TestClient,
    *,
    legal_name: str,
    trade_name: str,
    document: str,
    status: str = "active",
) -> dict:
    """Cria uma empresa para os cenários do dashboard."""

    response = client.post(
        "/api/companies",
        json={
            "legal_name": legal_name,
            "trade_name": trade_name,
            "document": document,
            "email": None,
            "phone": None,
            "status": status,
        },
    )

    assert response.status_code == 201
    return response.json()


def create_indicator(
    client: TestClient,
    *,
    company_id: str,
    name: str,
    unit: str,
    direction: str,
    target_value: str,
    status: str = "active",
) -> dict:
    """Cria um indicador para os cenários do dashboard."""

    response = client.post(
        "/api/indicators",
        json={
            "company_id": company_id,
            "name": name,
            "description": None,
            "unit": unit,
            "direction": direction,
            "target_value": target_value,
            "status": status,
        },
    )

    assert response.status_code == 201
    return response.json()


def create_measurement(
    client: TestClient,
    *,
    indicator_id: str,
    reference_date: str,
    actual_value: str,
    observation: str | None = None,
) -> dict:
    """Cria uma medição para os cenários do dashboard."""

    response = client.post(
        "/api/measurements",
        json={
            "indicator_id": indicator_id,
            "reference_date": reference_date,
            "actual_value": actual_value,
            "observation": observation,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_get_dashboard_overview_without_data(
    client: TestClient,
) -> None:
    """Retorna uma visão gerencial vazia quando não existem dados."""

    response = client.get("/api/dashboards/overview")

    assert response.status_code == 200

    data = response.json()

    assert data["totals"] == {
        "companies": 0,
        "indicators": 0,
        "measurements": 0,
    }
    assert data["companies_by_status"] == []
    assert data["indicators_by_status"] == []
    assert data["indicators"] == []


def test_get_dashboard_overview_with_consolidated_data(
    client: TestClient,
) -> None:
    """Consolida totais, status, indicadores e históricos."""

    active_company = create_company(
        client,
        legal_name="Empresa Alfa Ltda",
        trade_name="Alfa",
        document="11111111000111",
    )
    inactive_company = create_company(
        client,
        legal_name="Empresa Beta Ltda",
        trade_name="Beta",
        document="22222222000122",
        status="inactive",
    )

    revenue_indicator = create_indicator(
        client,
        company_id=active_company["id"],
        name="Faturamento",
        unit="BRL",
        direction="higher_is_better",
        target_value="1000.0000",
    )
    complaints_indicator = create_indicator(
        client,
        company_id=inactive_company["id"],
        name="Reclamações",
        unit="unidades",
        direction="lower_is_better",
        target_value="10.0000",
        status="inactive",
    )
    no_data_indicator = create_indicator(
        client,
        company_id=active_company["id"],
        name="Ticket médio",
        unit="BRL",
        direction="higher_is_better",
        target_value="100.0000",
    )

    first_revenue = create_measurement(
        client,
        indicator_id=revenue_indicator["id"],
        reference_date="2026-07-01",
        actual_value="800.0000",
        observation="Primeira apuração",
    )
    latest_revenue = create_measurement(
        client,
        indicator_id=revenue_indicator["id"],
        reference_date="2026-08-01",
        actual_value="1200.0000",
    )
    create_measurement(
        client,
        indicator_id=complaints_indicator["id"],
        reference_date="2026-08-01",
        actual_value="12.0000",
    )

    response = client.get("/api/dashboards/overview")

    assert response.status_code == 200

    data = response.json()

    assert data["totals"] == {
        "companies": 2,
        "indicators": 3,
        "measurements": 3,
    }
    assert data["companies_by_status"] == [
        {"status": "active", "count": 1},
        {"status": "inactive", "count": 1},
    ]
    assert data["indicators_by_status"] == [
        {"status": "active", "count": 2},
        {"status": "inactive", "count": 1},
    ]

    assert [
        (
            indicator["company_trade_name"],
            indicator["name"],
        )
        for indicator in data["indicators"]
    ] == [
        ("Alfa", "Faturamento"),
        ("Alfa", "Ticket médio"),
        ("Beta", "Reclamações"),
    ]

    revenue = data["indicators"][0]

    assert revenue["id"] == revenue_indicator["id"]
    assert revenue["company_id"] == active_company["id"]
    assert revenue["unit"] == "BRL"
    assert revenue["direction"] == "higher_is_better"
    assert Decimal(revenue["target_value"]) == Decimal("1000.0000")
    assert revenue["current_measurement"]["id"] == latest_revenue["id"]
    assert (
        Decimal(revenue["achievement_percentage"])
        == Decimal("120.0000")
    )
    assert revenue["situation"] == "on_target"
    assert [
        measurement["id"] for measurement in revenue["history"]
    ] == [
        first_revenue["id"],
        latest_revenue["id"],
    ]

    ticket = data["indicators"][1]

    assert ticket["id"] == no_data_indicator["id"]
    assert ticket["current_measurement"] is None
    assert ticket["achievement_percentage"] is None
    assert ticket["situation"] == "no_data"
    assert ticket["history"] == []

    complaints = data["indicators"][2]

    assert complaints["id"] == complaints_indicator["id"]
    assert (
        Decimal(complaints["achievement_percentage"])
        == Decimal("83.3333")
    )
    assert complaints["situation"] == "above_target"


def test_get_dashboard_overview_filters_company_and_period(
    client: TestClient,
) -> None:
    """Aplica conjuntamente os filtros de empresa e período."""

    first_company = create_company(
        client,
        legal_name="Empresa Gama Ltda",
        trade_name="Gama",
        document="33333333000133",
    )
    second_company = create_company(
        client,
        legal_name="Empresa Delta Ltda",
        trade_name="Delta",
        document="44444444000144",
    )

    first_indicator = create_indicator(
        client,
        company_id=first_company["id"],
        name="Disponibilidade",
        unit="%",
        direction="higher_is_better",
        target_value="99.0000",
    )
    second_indicator = create_indicator(
        client,
        company_id=second_company["id"],
        name="Incidentes",
        unit="unidades",
        direction="lower_is_better",
        target_value="5.0000",
    )

    create_measurement(
        client,
        indicator_id=first_indicator["id"],
        reference_date="2026-06-30",
        actual_value="97.0000",
    )
    included_measurement = create_measurement(
        client,
        indicator_id=first_indicator["id"],
        reference_date="2026-07-01",
        actual_value="98.0000",
    )
    create_measurement(
        client,
        indicator_id=first_indicator["id"],
        reference_date="2026-07-31",
        actual_value="99.0000",
    )
    create_measurement(
        client,
        indicator_id=first_indicator["id"],
        reference_date="2026-08-01",
        actual_value="100.0000",
    )
    create_measurement(
        client,
        indicator_id=second_indicator["id"],
        reference_date="2026-07-15",
        actual_value="4.0000",
    )

    response = client.get(
        "/api/dashboards/overview",
        params={
            "company_id": first_company["id"],
            "start_date": "2026-07-01",
            "end_date": "2026-07-01",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["totals"] == {
        "companies": 1,
        "indicators": 1,
        "measurements": 1,
    }
    assert data["companies_by_status"] == [
        {"status": "active", "count": 1},
    ]
    assert data["indicators_by_status"] == [
        {"status": "active", "count": 1},
    ]
    assert len(data["indicators"]) == 1

    indicator = data["indicators"][0]

    assert indicator["id"] == first_indicator["id"]
    assert indicator["current_measurement"]["id"] == included_measurement["id"]
    assert [item["id"] for item in indicator["history"]] == [
        included_measurement["id"],
    ]
    assert (
        Decimal(indicator["achievement_percentage"])
        == Decimal("98.9899")
    )
    assert indicator["situation"] == "below_target"


def test_get_dashboard_overview_rejects_invalid_period(
    client: TestClient,
) -> None:
    """Rejeita data inicial posterior à data final."""

    response = client.get(
        "/api/dashboards/overview",
        params={
            "start_date": "2026-08-01",
            "end_date": "2026-07-31",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": "invalid_dashboard_period",
        "message": "A data inicial não pode ser posterior à data final.",
    }


def test_get_dashboard_overview_rejects_unknown_company(
    client: TestClient,
) -> None:
    """Rejeita o filtro por uma empresa inexistente."""

    response = client.get(
        "/api/dashboards/overview",
        params={
            "company_id": "00000000-0000-0000-0000-000000000000",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "company_not_found"


def test_get_dashboard_overview_handles_zero_divisors(
    client: TestClient,
) -> None:
    """Evita divisão por zero no cálculo do percentual."""

    company = create_company(
        client,
        legal_name="Empresa Épsilon Ltda",
        trade_name="Épsilon",
        document="55555555000155",
    )

    higher_indicator = create_indicator(
        client,
        company_id=company["id"],
        name="Crescimento",
        unit="%",
        direction="higher_is_better",
        target_value="0.0000",
    )
    lower_indicator = create_indicator(
        client,
        company_id=company["id"],
        name="Falhas",
        unit="unidades",
        direction="lower_is_better",
        target_value="1.0000",
    )

    create_measurement(
        client,
        indicator_id=higher_indicator["id"],
        reference_date="2026-08-01",
        actual_value="1.0000",
    )
    create_measurement(
        client,
        indicator_id=lower_indicator["id"],
        reference_date="2026-08-01",
        actual_value="0.0000",
    )

    response = client.get("/api/dashboards/overview")

    assert response.status_code == 200

    indicators = {
        indicator["name"]: indicator
        for indicator in response.json()["indicators"]
    }

    assert indicators["Crescimento"]["achievement_percentage"] is None
    assert indicators["Crescimento"]["situation"] == "on_target"
    assert indicators["Falhas"]["achievement_percentage"] is None
    assert indicators["Falhas"]["situation"] == "on_target"