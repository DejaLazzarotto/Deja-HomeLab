# Migrations — Deja Indicadores API

Este diretório contém as migrations versionadas do banco de dados do Deja Indicadores.

As migrations são executadas pelo Alembic e utilizam a conexão MySQL definida no arquivo `.env` local.

## Organização

- `env.py`: configuração de execução do Alembic;
- `script.py.mako`: modelo para geração de migrations;
- `versions/`: histórico versionado das alterações do banco.

As credenciais reais de acesso ao banco não devem ser versionadas.