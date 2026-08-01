# 10. Integração com Administration Platform

## Objetivo

Definir a arquitetura de integração entre a Administration Console e a Administration Platform, estabelecendo a separação institucional entre a camada de experiência administrativa e a camada responsável pelas operações administrativas da Deja Platform.

---

## Princípios da Integração

A integração é baseada nos seguintes princípios:

- separação entre interface e domínio;
- consumo exclusivo de contratos públicos;
- baixo acoplamento;
- independência de implementação;
- rastreabilidade completa;
- evolução independente;
- segurança institucional.

A Administration Console nunca acessa implementações internas da Administration Platform.

---

## Papéis Arquiteturais

### Administration Console

Responsável por:

- experiência administrativa;
- dashboards;
- navegação;
- formulários;
- componentes visuais;
- interação do administrador;
- coordenação da interface.

---

### Administration Platform

Responsável por:

- regras administrativas;
- validações;
- orquestração das operações;
- execução das ações administrativas;
- coordenação entre capacidades;
- auditoria das operações;
- gerenciamento administrativo da plataforma.

---

## Fluxo de Comunicação

O fluxo institucional ocorre da seguinte forma:

```
Administrador
        │
        ▼
Administration Console
        │
        ▼
Administration Platform
        │
        ▼
Capacidades Institucionais
```

Toda solicitação administrativa é iniciada pela Console, processada pela Administration Platform e encaminhada às capacidades responsáveis.

---

## Contratos Públicos

A integração ocorre exclusivamente por contratos institucionais publicados.

Entre eles:

- APIs administrativas;
- comandos administrativos;
- consultas;
- eventos;
- notificações;
- serviços públicos.

Os contratos representam a única forma de comunicação entre ambas as capacidades.

---

## Sincronização

A Console sincroniza informações administrativas por meio de:

- consultas sob demanda;
- atualização periódica;
- eventos institucionais;
- notificações operacionais.

A estratégia depende da natureza de cada informação.

---

## Tratamento de Erros

Toda falha retornada pela Administration Platform deve ser apresentada de forma consistente ao administrador.

A Console não interpreta regras de negócio nem altera resultados produzidos pela Platform.

---

## Benefícios Arquiteturais

Esta separação proporciona:

- desacoplamento entre interface e domínio;
- reutilização da camada administrativa;
- evolução independente;
- maior segurança;
- facilidade de manutenção;
- escalabilidade;
- padronização institucional;
- integração consistente entre capacidades.