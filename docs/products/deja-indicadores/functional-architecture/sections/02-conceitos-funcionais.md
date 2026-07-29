# 02. Conceitos Funcionais

## Objetivo

Este documento estabelece os conceitos institucionais utilizados pela Arquitetura Funcional da Deja Indicadores.

Seu propósito é definir uma linguagem única e padronizada para representar a organização funcional do produto, garantindo consistência entre planejamento, desenvolvimento, testes e documentação.

Todos os documentos produzidos durante o ciclo de vida do produto deverão utilizar obrigatoriamente os conceitos definidos nesta seção.

---

# Visão Geral

A Arquitetura Funcional organiza o produto através de um conjunto de elementos hierárquicos e complementares.

Cada elemento possui responsabilidades específicas e participa do modelo oficial de rastreabilidade da Deja Platform.

Os principais conceitos são:

- Capability (CAP)
- Epic (EP)
- Functional Module (FM)
- Feature (FE)
- Functional Flow (FF)
- Functional Specification (FS)
- Release (REL)

---

# Capability (CAP)

Uma Capability representa uma capacidade de negócio que o produto deve oferecer aos seus usuários.

As Capabilities descrevem resultados esperados pelo negócio e permanecem relativamente estáveis ao longo da evolução do produto.

Características:

- representam necessidades de negócio;
- independem da implementação;
- podem originar diversos Épicos;
- são definidas durante o Capability Map.

Exemplo:

```
CAP-003

Gerenciamento de Indicadores
```

---

# Epic (EP)

Um Epic representa uma iniciativa funcional de grande porte responsável por implementar parte de uma Capability.

Um Épico normalmente agrupa diversas Features relacionadas.

Características:

- possui alto nível de abstração;
- representa uma grande entrega funcional;
- organiza o planejamento incremental do produto.

Exemplo:

```
EP-002

Implantação da Gestão de Indicadores
```

---

# Functional Module (FM)

Um Functional Module representa um agrupamento lógico de funcionalidades relacionadas.

Os módulos organizam o produto sob a perspectiva do negócio, independentemente da arquitetura técnica.

Características:

- organizam áreas funcionais do produto;
- agrupam Features relacionadas;
- permanecem relativamente estáveis ao longo da evolução do sistema.

Exemplo:

```
FM-IND

Indicadores
```

---

# Feature (FE)

Uma Feature representa uma funcionalidade percebida pelo usuário e entregue pelo produto.

Ela constitui a menor unidade funcional planejada para implementação e entrega de valor.

Características:

- produz valor perceptível;
- pertence a um único Módulo Funcional;
- pode participar de uma ou mais Releases;
- possui uma Especificação Funcional própria.

Exemplo:

```
FE-014

Cadastrar Indicador
```

---

# Functional Flow (FF)

Um Functional Flow representa a sequência lógica de atividades necessárias para execução de uma Feature.

Fluxos descrevem o comportamento esperado do produto sob a perspectiva do usuário, sem definir detalhes de interface ou implementação.

Características:

- descrevem processos funcionais;
- independem de tecnologia;
- podem ser reutilizados por diferentes Features.

Exemplo:

```
FF-005

Cadastrar Indicador
    ↓
Validar Dados
    ↓
Salvar Indicador
    ↓
Disponibilizar para Uso
```

---

# Functional Specification (FS)

Uma Functional Specification descreve detalhadamente como uma Feature deverá se comportar.

Ela constitui o principal artefato utilizado durante a implementação.

Uma Especificação Funcional poderá conter:

- objetivo;
- escopo;
- regras de negócio;
- fluxos;
- critérios de aceitação;
- restrições;
- dependências;
- rastreabilidade.

Cada Feature possui exatamente uma Especificação Funcional principal.

Exemplo:

```
FS-014

Especificação Funcional
Cadastrar Indicador
```

---

# Release (REL)

Uma Release representa um agrupamento planejado de Features que serão disponibilizadas em conjunto.

As Releases organizam o planejamento das entregas do produto.

Uma Release não faz parte da hierarquia funcional.

Ela atua como mecanismo de planejamento.

Características:

- agrupa Features;
- organiza entregas;
- permite evolução incremental;
- pode conter Features de diferentes módulos.

Exemplo:

```
REL-001

Produto Mínimo Viável
```

---

# Relação entre os Conceitos

Os conceitos definidos nesta arquitetura se relacionam da seguinte forma:

```
Capability
        │
        ▼
Epic
        │
        ▼
Functional Module
        │
        ▼
Feature
        │
        ▼
Functional Flow
        │
        ▼
Functional Specification
```

As Releases agrupam Features para fins de planejamento e entrega.

---

# Considerações Finais

Os conceitos apresentados neste documento constituem a base da Arquitetura Funcional da Deja Indicadores.

Toda documentação produzida durante a evolução do produto deverá utilizar obrigatoriamente esta terminologia, preservando consistência, rastreabilidade e padronização entre todas as fases do ciclo de desenvolvimento.