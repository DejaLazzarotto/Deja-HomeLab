# ADR-004 — Deja Platform CLI

## Status

Accepted

## Data

2026-06-25

---

# Contexto

A Deja Platform começou a evoluir de uma plataforma documentada para uma plataforma operacional.

Inicialmente foi considerada a criação de scripts independentes para tarefas como health check, backup, deploy, restore e inventário.

Entretanto, scripts isolados tendem a gerar duplicidade, inconsistência e dificuldade de manutenção conforme a plataforma cresce.

---

# Decisão

A automação operacional da Deja Platform será centralizada em uma CLI própria chamada **Deja Platform CLI**.

Essa CLI será o ponto único de entrada para comandos administrativos e operacionais da plataforma.

---

# Comando Principal

Inicialmente, a CLI será executada a partir do repositório:

```bash
./platform/platform
```

Futuramente poderá ser instalada globalmente como:

```bash
platform
```

---

# Estrutura

```text
platform/
├── platform
├── config
│   └── deja-platform.conf
├── lib
│   ├── common.sh
│   ├── colors.sh
│   ├── logger.sh
│   └── output.sh
└── commands
    ├── version.sh
    ├── health.sh
    ├── inventory.sh
    ├── services.sh
    ├── backup.sh
    ├── deploy.sh
    └── restore.sh
```

---

# Subcomandos previstos

```bash
platform version
platform health
platform inventory
platform services
platform backup
platform deploy
platform restore
```

---

# Consequências

## Benefícios

* Ponto único de entrada operacional.
* Reutilização de bibliotecas comuns.
* Padronização de saída.
* Facilidade de manutenção.
* Evolução incremental.
* Redução de scripts soltos.

## Desvantagens

* Requer disciplina na organização dos comandos.
* Exige cuidado para não transformar a CLI em uma ferramenta complexa demais.

---

# Diretrizes

Cada novo comando da CLI deverá possuir:

* objetivo claro;
* documentação;
* comportamento previsível;
* mensagens legíveis;
* validação manual;
* evolução incremental.

---

# Relação com outras ADRs

* ADR-001 — Platform Architecture
* ADR-002 — NGINX como Edge Layer
* ADR-003 — Padrão de Publicação de Aplicações
