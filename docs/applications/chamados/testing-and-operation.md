# Testes e operação — Deja Chamados

## Execução local

Backend:

- caminho: `deja-indicadores-api`
- endereço: `127.0.0.1:8000`

Frontend:

- caminho: `workspace`
- endereço: `http://localhost:4200`

## Validação

Fluxo recomendado antes de concluir alterações:

- build do frontend;
- testes do frontend;
- testes do backend;
- validação visual;
- `git diff --check`;
- `git status`;
- `git diff --stat`;
- `git diff --numstat`.

## Cobertura atual

O módulo possui testes do backend e do frontend cobrindo as principais regras de negócio, repositórios, autorização, componentes e fluxos operacionais.

## Observação

Os números de testes não são fixados neste documento, pois novas coberturas podem ser adicionadas durante a auditoria.
