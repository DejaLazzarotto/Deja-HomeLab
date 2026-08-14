# 04. Modelo de Segurança

## Objetivo

Esta seção descreve o modelo conceitual de segurança adotado pela Deja Platform.

O modelo define como identidades, recursos, políticas e operações são relacionados para garantir controle, proteção e rastreabilidade em toda a plataforma.

---

## Conceito central

O modelo de segurança da Deja Platform é baseado na relação entre:

- identidade;
- contexto;
- recurso;
- política;
- decisão de acesso;
- operação;
- auditoria.

Toda interação relevante deve passar por uma avaliação de segurança antes de ser executada.

---

## Entidades de segurança

O modelo reconhece diferentes tipos de entidades:

### Usuários

Representam pessoas que utilizam a plataforma.

Podem possuir:

- identidade;
- perfil;
- permissões;
- organizações associadas;
- histórico de atividades.

---

### Serviços

Representam componentes internos ou externos que executam operações.

Exemplos:

- APIs;
- serviços internos;
- workers;
- integrações.

---

### Componentes

Representam módulos arquiteturais da Deja Platform.

Exemplos:

- Execution Engine;
- Intelligence Core;
- Workspace Runtime.

---

### Agentes

Representam entidades inteligentes ou automatizadas capazes de executar ações.

Exemplos:

- AI Assistant;
- agentes especializados;
- processos automatizados.

---

## Modelo de acesso

O acesso a recursos segue o fluxo:

Identity
↓
Authentication
↓
Context Evaluation
↓
Policy Evaluation
↓
Authorization Decision
↓
Operation Execution
↓
Audit Registration


Cada etapa produz informações utilizadas pela próxima etapa.

---

## Recursos protegidos

O modelo considera como recursos protegidos:

- dados;
- APIs;
- serviços;
- workflows;
- execuções;
- dashboards;
- configurações;
- modelos analíticos;
- credenciais;
- segredos.

---

## Políticas de segurança

As políticas definem as regras utilizadas para decidir acessos.

Uma política pode considerar:

- identidade;
- papel;
- organização;
- recurso;
- operação;
- localização;
- horário;
- nível de risco;
- contexto operacional.

---

## Decisão de acesso

A decisão de acesso deve ser explícita e rastreável.

Possíveis resultados:

- permitido;
- negado;
- condicionado;
- requer validação adicional.

Toda decisão relevante deve possuir justificativa registrada.

---

## Controle baseado em políticas

O Security utiliza um modelo orientado a políticas.

Esse modelo permite:

- centralização das regras;
- atualização independente;
- auditoria das decisões;
- aplicação consistente.

---

## Rastreabilidade de segurança

Toda operação protegida deve gerar informações suficientes para reconstruir:

- identidade responsável;
- recurso acessado;
- política aplicada;
- decisão tomada;
- resultado obtido.

Essas informações podem ser integradas ao:

- Execution Log;
- Execution History;
- Observability.

---

## Segurança e execução

O Security integra-se ao ciclo operacional da plataforma.

Antes de uma execução:

- a identidade é validada;
- permissões são verificadas;
- políticas são avaliadas.

Durante a execução:

- acessos são controlados;
- eventos relevantes são registrados.

Após a execução:

- resultados são auditados;
- registros são preservados.

---

## Superfície pública da API do Deja Indicadores

A superfície pública funcional da API deve permanecer limitada ao estritamente necessário.

No MVP comercial, são públicas intencionalmente:

- `GET /health`, para verificação de disponibilidade;
- `POST /api/v1/auth/login`, para autenticação e emissão do Bearer token.

As demais rotas funcionais exigem identidade autenticada e aplicam, conforme a operação:

- validação de papel na entrada HTTP;
- revalidação na camada de serviço;
- resolução do escopo institucional;
- filtragem persistente no SQL.

A documentação interativa da API segue a política do ambiente:

- em `development` e `testing`, `/docs`, `/docs/oauth2-redirect`, `/redoc` e `/openapi.json` permanecem disponíveis para desenvolvimento e validação;
- em `production`, esses endpoints não são registrados e retornam HTTP 404;
- a desativação em produção reduz a exposição desnecessária da estrutura e dos contratos internos da API.

Essa política não substitui autenticação nem autorização das rotas funcionais.

---

## Modelo institucional

O modelo de segurança estabelece que toda operação na Deja Platform deve possuir:

- identidade conhecida;
- autorização válida;
- política aplicável;
- registro rastreável.

Esse modelo garante segurança consistente para evolução da plataforma em ambientes corporativos.