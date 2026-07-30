# Catálogo Institucional de Features

## Objetivo

Este documento constitui o catálogo oficial de Features da Deja Indicadores.

Seu objetivo é centralizar a identificação, organização, rastreabilidade e o status de todas as Features funcionais do produto, servindo como referência para planejamento, documentação, desenvolvimento e governança.

Este catálogo é a visão executiva da arquitetura funcional do produto e complementa a documentação individual existente em cada diretório de Feature.

---

# Organização

Cada Feature possui obrigatoriamente:

- um identificador único (FE-XXX);
- um diretório próprio;
- um Documento Mestre (`feature.md`);
- uma coleção de Functional Specifications;
- rastreabilidade completa com Capabilities, Épicos e Módulos Funcionais.

---

# Catálogo de Features

| Feature | Nome | Módulo Funcional | Épico | Functional Specifications | Status | Versão |
|----------|------|------------------|--------|---------------------------|--------|---------|
| FE-001 | Indicadores | FM-001 — Gestão de Indicadores | EP-001 / EP-002 | 10 | Documentada | 1.0 |

---

# Status das Features

Os seguintes estados são utilizados institucionalmente:

| Status | Descrição |
|----------|-----------|
| Planejada | Feature identificada, ainda sem documentação. |
| Em documentação | Documentação funcional em elaboração. |
| Documentada | Documentação funcional concluída. |
| Em implementação | Desenvolvimento iniciado. |
| Em validação | Em testes funcionais. |
| Concluída | Implementação validada e incorporada ao produto. |
| Descontinuada | Feature removida ou substituída. |

---

# Convenções

Toda Feature deve:

- possuir identificador único;
- pertencer a um único Módulo Funcional;
- estar vinculada a um ou mais Épicos;
- atender uma ou mais Capabilities;
- possuir pelo menos uma Functional Specification;
- manter independência da Arquitetura Técnica;
- utilizar os templates institucionais.

---

# Rastreabilidade

Toda Feature participa da cadeia institucional:

```
Capability
    ↓
Epic
    ↓
Functional Module
    ↓
Feature
    ↓
Functional Function
    ↓
Functional Specification
    ↓
Arquitetura Técnica
    ↓
Código
    ↓
Testes
    ↓
Documentação
```

---

# Evolução

Novas Features deverão ser adicionadas exclusivamente neste catálogo antes do início de sua documentação funcional.

A inclusão de uma nova Feature deve atualizar:

- este catálogo;
- o diretório `features/`;
- a documentação do Módulo Funcional correspondente;
- a rastreabilidade com Capabilities e Épicos.

---

# Governança

A criação, alteração ou descontinuação de Features deve preservar:

- unicidade do identificador;
- consistência da nomenclatura;
- integridade da rastreabilidade;
- conformidade com os templates institucionais;
- independência da Arquitetura Técnica.

---

# Histórico

| Versão | Data | Alterações |
|---------|------|------------|
| 1.0 | 2026-07-30 | Criação do Catálogo Institucional de Features e registro da FE-001 como primeira Feature oficial da Deja Indicadores. |