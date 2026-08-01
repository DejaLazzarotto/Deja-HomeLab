# 04. Modelo de Aplicações

## Objetivo

A Workspace Applications define um modelo institucional único para aplicações executadas no Workspace da Deja Platform.

Esse modelo estabelece a estrutura, identidade, contratos, metadados e comportamento esperado de qualquer aplicação, independentemente da tecnologia utilizada em sua implementação.

---

## Aplicação como unidade institucional

Uma aplicação representa uma capacidade funcional disponibilizada aos usuários através do Workspace.

Cada aplicação é tratada como um recurso institucional independente, possuindo:

- identidade própria;
- ciclo de vida próprio;
- metadados institucionais;
- contratos públicos;
- contexto de execução isolado;
- versionamento independente.

A infraestrutura do Workspace não depende da implementação interna da aplicação.

---

## Identidade da aplicação

Toda aplicação deve possuir uma identidade institucional única.

Essa identidade é composta por:

- Application ID;
- nome;
- versão;
- fornecedor;
- categoria;
- descrição;
- ícone;
- tipo de aplicação;
- módulo de origem.

A identidade permanece estável durante todo o ciclo de vida da aplicação.

---

## Metadados institucionais

Os metadados descrevem as características necessárias para registro, descoberta e execução.

Entre eles:

- versão mínima da plataforma;
- versão do Workspace;
- dependências;
- capacidades requeridas;
- permissões necessárias;
- políticas de execução;
- requisitos de segurança;
- requisitos de observabilidade;
- compatibilidade entre versões.

Os metadados constituem o contrato institucional da aplicação.

---

## Contratos públicos

Toda aplicação comunica-se exclusivamente através de contratos públicos.

Os contratos permitem:

- inicialização;
- encerramento;
- integração com o Workspace Runtime;
- acesso aos serviços institucionais;
- recebimento de eventos;
- publicação de eventos.

É proibido qualquer acesso direto às implementações internas da plataforma.

---

## Contexto de execução

Cada aplicação executa em um contexto isolado fornecido pela Workspace Applications.

O contexto pode disponibilizar:

- organização;
- tenant;
- ambiente;
- usuário autenticado;
- permissões efetivas;
- configuração;
- serviços institucionais;
- APIs públicas;
- recursos do Workspace.

Esse contexto é criado antes da inicialização e destruído durante o encerramento da aplicação.

---

## Independência entre aplicações

Aplicações não mantêm dependências diretas entre si.

Toda colaboração ocorre por meio de:

- eventos institucionais;
- contratos públicos;
- serviços registrados;
- APIs da plataforma.

Esse modelo elimina acoplamentos indevidos e preserva a evolução independente de cada aplicação.

---

## Compatibilidade arquitetural

Toda aplicação deve permanecer compatível com a arquitetura institucional vigente.

A Workspace Applications valida:

- versões suportadas;
- contratos obrigatórios;
- dependências;
- políticas de segurança;
- requisitos de execução.

Aplicações incompatíveis não podem ser carregadas pelo Workspace Runtime.

---

## Benefícios do modelo

A adoção desse modelo proporciona:

- padronização institucional;
- baixo acoplamento;
- evolução independente;
- facilidade de manutenção;
- reutilização de infraestrutura;
- carregamento previsível;
- integração consistente;
- escalabilidade;
- compatibilidade entre versões;
- governança arquitetural contínua.