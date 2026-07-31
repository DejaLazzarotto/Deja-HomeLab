# 05. Componentes

## Objetivo

Esta seção descreve os componentes arquiteturais que formam o Security da Deja Platform.

Cada componente possui responsabilidades específicas, mantendo separação de responsabilidades, baixo acoplamento e evolução independente.

---

## Visão geral dos componentes

O Security é composto pelos seguintes componentes institucionais:

- Identity Service;
- Authentication Service;
- Authorization Service;
- Policy Engine;
- Credential Manager;
- Secrets Manager;
- Encryption Service;
- Security Audit Service;
- Security Policy Registry;
- Security Governance Service.

---

# Identity Service

## Responsabilidade

O Identity Service é responsável pelo gerenciamento das identidades reconhecidas pela plataforma.

---

## Capacidades

Inclui:

- criação de identidades;
- atualização de atributos;
- associação de metadados;
- identificação de usuários;
- identificação de serviços;
- identificação de componentes.

---

## Integrações

É utilizado por:

- Authentication Service;
- Authorization Service;
- Audit Service;
- Observability.

---

# Authentication Service

## Responsabilidade

O Authentication Service valida a identidade de entidades que solicitam acesso à plataforma.

---

## Capacidades

Inclui:

- autenticação de usuários;
- autenticação de serviços;
- validação de tokens;
- gerenciamento de sessões;
- integração com provedores externos.

---

## Objetivo

Garantir que somente entidades autenticadas possam participar dos fluxos autorizados.

---

# Authorization Service

## Responsabilidade

O Authorization Service determina se uma identidade possui permissão para executar determinada operação.

---

## Capacidades

Inclui:

- avaliação de permissões;
- validação de políticas;
- controle de recursos;
- decisões de acesso.

---

# Policy Engine

## Responsabilidade

O Policy Engine executa a avaliação das políticas de segurança.

---

## Capacidades

Inclui:

- interpretação de regras;
- avaliação contextual;
- decisões dinâmicas;
- versionamento de políticas.

---

## Característica arquitetural

O Policy Engine mantém as regras separadas dos componentes que utilizam segurança.

---

# Credential Manager

## Responsabilidade

O Credential Manager controla o ciclo de vida das credenciais utilizadas pela plataforma.

---

## Capacidades

Inclui:

- criação;
- armazenamento seguro;
- renovação;
- expiração;
- revogação.

---

# Secrets Manager

## Responsabilidade

O Secrets Manager protege informações sensíveis utilizadas por serviços e integrações.

---

## Exemplos de segredos

- tokens;
- chaves;
- certificados;
- credenciais externas;
- configurações protegidas.

---

# Encryption Service

## Responsabilidade

O Encryption Service fornece mecanismos de proteção criptográfica.

---

## Capacidades

Inclui:

- criptografia de dados;
- gerenciamento de chaves;
- proteção de comunicação;
- validação de integridade.

---

# Security Audit Service

## Responsabilidade

O Security Audit Service registra atividades relacionadas à segurança.

---

## Capacidades

Inclui:

- registros de acesso;
- alterações de políticas;
- eventos de autenticação;
- eventos de autorização;
- operações sensíveis.

---

## Integração

Integra-se diretamente com:

- Execution Log;
- Execution History;
- Observability.

---

# Security Policy Registry

## Responsabilidade

O Security Policy Registry mantém o catálogo institucional das políticas de segurança.

---

## Capacidades

Inclui:

- armazenamento de políticas;
- versionamento;
- publicação;
- consulta;
- histórico de alterações.

---

# Security Governance Service

## Responsabilidade

O Security Governance Service coordena padrões e controles institucionais.

---

## Capacidades

Inclui:

- regras corporativas;
- requisitos de conformidade;
- padrões de segurança;
- evolução arquitetural.

---

# Relacionamento entre componentes

O fluxo principal é:
