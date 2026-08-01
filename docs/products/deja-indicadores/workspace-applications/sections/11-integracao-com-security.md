# 11. Integração com Security

## Objetivo

A Workspace Applications integra-se à capacidade institucional Security para garantir que todas as aplicações executadas no Workspace operem dentro das políticas oficiais de autenticação, autorização, identidade, permissões e proteção definidas pela Deja Platform.

A Workspace Applications nunca implementa mecanismos próprios de segurança, atuando exclusivamente como consumidora dos serviços disponibilizados pela Security.

---

## Princípios

A integração baseia-se nos seguintes princípios:

- Security é a autoridade institucional sobre segurança;
- autenticação é centralizada;
- autorização é centralizada;
- permissões são avaliadas pela Security;
- aplicações não implementam controle próprio de acesso;
- todo acesso é auditável;
- políticas são aplicadas de forma uniforme;
- contratos públicos são obrigatórios.

---

## Responsabilidades da Security

Compete exclusivamente à Security:

- autenticação de usuários;
- autorização;
- gerenciamento de identidades;
- emissão e validação de credenciais;
- gerenciamento de permissões;
- políticas de acesso;
- proteção de recursos;
- auditoria de segurança.

---

## Responsabilidades da Workspace Applications

Compete à Workspace Applications:

- solicitar validações de segurança;
- consumir informações de identidade;
- respeitar permissões concedidas;
- fornecer contexto da aplicação;
- impedir execução de aplicações não autorizadas;
- propagar eventos de segurança quando necessário.

Nenhuma decisão de autorização é tomada pela Workspace Applications.

---

## Fluxo de integração

O processo institucional ocorre da seguinte forma:

```text
Usuário
      │
      ▼
Security
      │
      ▼
Autenticação
      │
      ▼
Autorização
      │
      ▼
Workspace Applications
      │
      ▼
Workspace Runtime
      │
      ▼
Aplicação
```

Toda validação ocorre antes da disponibilização da aplicação ao usuário.

---

## Contexto de segurança

Durante a execução, cada aplicação recebe um contexto de segurança contendo apenas as informações necessárias para sua operação.

Esse contexto pode incluir:

- identidade do usuário;
- organização;
- tenant;
- ambiente;
- papéis;
- permissões efetivas;
- políticas aplicáveis.

A aplicação não possui acesso às estruturas internas da Security.

---

## Controle de permissões

Antes da ativação de uma aplicação são avaliados:

- permissões necessárias;
- políticas organizacionais;
- restrições do tenant;
- ambiente de execução;
- requisitos institucionais.

Aplicações que não atendem aos requisitos permanecem indisponíveis.

---

## Auditoria

Todos os eventos relevantes são registrados pela Security e podem ser correlacionados com informações produzidas pela Workspace Applications.

Entre eles:

- tentativas de acesso;
- carregamentos autorizados;
- bloqueios;
- falhas de autorização;
- encerramentos por políticas de segurança.

---

## Benefícios

A integração institucional proporciona:

- segurança centralizada;
- eliminação de duplicidade de controles;
- padronização das políticas;
- rastreabilidade completa;
- isolamento entre aplicações;
- maior governança;
- conformidade arquitetural;
- evolução independente entre Workspace Applications e Security.