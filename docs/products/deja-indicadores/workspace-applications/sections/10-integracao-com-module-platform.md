# 10. Integração com Module Platform

## Objetivo

A Workspace Applications integra-se à Module Platform para permitir que aplicações sejam distribuídas, instaladas, registradas, atualizadas e removidas de forma padronizada, preservando o modelo modular da Deja Platform.

A Module Platform permanece responsável pelo ciclo de vida dos módulos, enquanto a Workspace Applications administra exclusivamente as aplicações executadas no Workspace.

---

## Responsabilidades

### Module Platform

A Module Platform é responsável por:

- distribuição de módulos;
- instalação;
- atualização;
- remoção;
- gerenciamento de versões;
- resolução de dependências entre módulos;
- publicação de capacidades.

---

### Workspace Applications

A Workspace Applications é responsável por:

- registro das aplicações do Workspace;
- descoberta das aplicações instaladas;
- carregamento;
- inicialização;
- integração com o Workspace Runtime;
- gerenciamento do ciclo de vida das aplicações;
- administração operacional.

---

## Fluxo de integração

O relacionamento entre ambas as capacidades ocorre conforme o fluxo institucional:

```text
Module Package
        │
        ▼
Module Platform
        │
        ▼
Instalação
        │
        ▼
Registro da Aplicação
        │
        ▼
Workspace Applications
        │
        ▼
Application Discovery
        │
        ▼
Application Loader
        │
        ▼
Workspace Runtime
```

Cada etapa possui contratos públicos próprios e responsabilidades claramente definidas.

---

## Descoberta de aplicações

Após a instalação de um módulo pela Module Platform, a Workspace Applications identifica automaticamente as aplicações disponibilizadas por esse módulo.

Durante esse processo são avaliados:

- identidade institucional;
- metadados;
- versões;
- dependências;
- compatibilidade com o Workspace.

Somente aplicações válidas são registradas.

---

## Atualizações

Quando um módulo é atualizado, a Workspace Applications reavalia:

- contratos públicos;
- metadados;
- compatibilidade;
- dependências;
- políticas de execução.

Caso sejam identificadas incompatibilidades, a aplicação não é disponibilizada para execução.

---

## Remoção

A remoção de um módulo desencadeia a remoção controlada das aplicações associadas.

O processo inclui:

- encerramento das aplicações em execução;
- descarregamento;
- remoção dos registros;
- atualização do catálogo institucional;
- limpeza do contexto operacional.

Esse procedimento preserva a consistência da plataforma.

---

## Benefícios da integração

A integração entre Workspace Applications e Module Platform proporciona:

- instalação automatizada de aplicações;
- descoberta institucional;
- carregamento padronizado;
- gerenciamento consistente de versões;
- desacoplamento entre infraestrutura e funcionalidades;
- evolução independente das capacidades;
- maior governança arquitetural;
- escalabilidade da plataforma.

A separação clara de responsabilidades garante uma arquitetura modular, previsível e compatível com os princípios institucionais da Deja Platform.