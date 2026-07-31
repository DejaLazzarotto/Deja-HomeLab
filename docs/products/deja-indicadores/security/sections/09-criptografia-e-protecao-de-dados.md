# 09. Criptografia e Proteção de Dados

## Objetivo

Esta seção descreve a arquitetura institucional de criptografia e proteção de dados do Security da Deja Platform.

A camada de proteção de dados estabelece os mecanismos responsáveis por preservar confidencialidade, integridade e segurança das informações manipuladas pela plataforma.

---

# Princípios de proteção de dados

A proteção de dados segue os seguintes princípios:

- proteção desde a origem;
- criptografia adequada ao contexto;
- controle de acesso;
- minimização de exposição;
- rastreabilidade de utilização;
- governança contínua.

---

# Encryption Service

## Responsabilidade

O Encryption Service fornece capacidades criptográficas reutilizáveis para os componentes da Deja Platform.

---

## Capacidades

Inclui:

- criptografia de dados;
- descriptografia controlada;
- assinatura digital;
- validação de integridade;
- gerenciamento de chaves;
- proteção de comunicação.

---

# Dados protegidos

O Security considera diferentes categorias de proteção:

## Dados armazenados

Informações persistidas em:

- bancos de dados;
- arquivos;
- armazenamentos analíticos;
- históricos operacionais.

---

## Dados em trânsito

Informações transmitidas entre:

- serviços internos;
- APIs;
- integrações externas;
- componentes distribuídos.

---

## Dados em processamento

Informações temporariamente utilizadas por:

- serviços;
- workflows;
- engines;
- agentes inteligentes.

---

# Gestão de chaves criptográficas

As chaves criptográficas devem possuir ciclo de vida controlado.

O ciclo contempla:
