# 15. Public API

A Public API estabelece a superfície oficial de integração do Intelligence Core.

Seu objetivo é disponibilizar contratos institucionais para consumo pelos Engines especializados e pelos demais componentes da Deja Platform, preservando o encapsulamento da implementação interna do núcleo.

A Public API constitui o único mecanismo autorizado para acesso às capacidades do Intelligence Core.

## Responsabilidades

Compete à Public API:

- disponibilizar contratos públicos do Core;
- definir interfaces institucionais de integração;
- preservar o encapsulamento das implementações internas;
- garantir estabilidade entre versões;
- suportar evolução incremental da plataforma;
- permitir integração de novos Engines;
- fornecer acesso padronizado aos componentes institucionais.

## Capacidades disponibilizadas

A Public API disponibiliza acesso às principais capacidades do Intelligence Core.

```text
                  Public API
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
 Runtime           Context          Pipeline
    │                  │                  │
    ├─────────────┬────┴────┬─────────────┤
    │             │         │             │
 Event Bus    Services   Registry   Lifecycle
    │             │         │             │
    ├─────────────┼─────────┼─────────────┤
    │             │         │             │
 Extensions  Configuration Observability Traceability
```

Cada capacidade é disponibilizada exclusivamente por meio dos contratos públicos definidos pelo Intelligence Core.

## Consumidores

A Public API pode ser utilizada por:

- Knowledge Base;
- Indicator Catalog;
- Diagnostic Engine;
- Recommendation Engine;
- Decision Engine;
- Execution Engine;
- futuros Engines;
- componentes da Deja Platform autorizados.

Todos os consumidores interagem apenas com contratos públicos, permanecendo independentes da implementação interna do Core.

## Compatibilidade

A evolução da Public API deverá preservar compatibilidade com versões anteriores sempre que possível.

Alterações incompatíveis deverão seguir o processo institucional de versionamento arquitetural, garantindo previsibilidade para os componentes consumidores.

## Encapsulamento

A implementação interna do Intelligence Core não faz parte da Public API.

Componentes externos não devem acessar estruturas internas, estados privados ou mecanismos de implementação específicos do núcleo.

Essa separação reduz o acoplamento e permite evolução contínua da infraestrutura sem impacto direto sobre os consumidores.

## Evolução

Novos contratos públicos poderão ser incorporados à Public API conforme a evolução da Deja Indicadores.

Toda ampliação deverá preservar os princípios arquiteturais do Intelligence Core, mantendo estabilidade, simplicidade e baixo acoplamento entre os componentes do ecossistema.