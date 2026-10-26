"""Isolamento dos testes de integração MySQL do VIVARO."""

import pytest


@pytest.fixture()
def clean_database():
    """Impede a limpeza automática global neste diretório.

    Os testes de integração administram suas próprias tabelas e registros.
    """
    yield
