# Deja Platform

## Visão Geral

A **Deja Platform** é a plataforma de infraestrutura utilizada para desenvolvimento, implantação, hospedagem, monitoramento e manutenção das aplicações desenvolvidas por Dejair Lazzarotto.

Ela foi projetada para servir como base permanente para projetos pessoais, acadêmicos e profissionais, seguindo princípios de arquitetura de software, DevOps, documentação técnica, segurança e observabilidade.

Embora atualmente seja composta por uma única VPS em produção, toda a arquitetura foi concebida para permitir crescimento horizontal, suportando novos servidores, novos serviços e novas aplicações sem necessidade de reorganização da documentação.

---

# Objetivos

A plataforma possui os seguintes objetivos:

* Centralizar a hospedagem das aplicações.
* Padronizar processos de desenvolvimento e implantação.
* Garantir segurança e rastreabilidade.
* Facilitar manutenção e evolução.
* Servir como ambiente permanente de estudos e experimentação.
* Demonstrar competências técnicas através de uma infraestrutura real.

---

# Arquitetura Conceitual

A plataforma está organizada em cinco domínios principais.

## Development

Responsável pela criação do software.

Inclui:

* Windows
* Visual Studio Code
* Git
* Projetos locais
* Testes
* Versionamento

Todo desenvolvimento ocorre localmente.

Nenhuma aplicação é desenvolvida diretamente na infraestrutura de produção.

---

## Infrastructure

Responsável pelos recursos fundamentais da plataforma.

Inclui:

* Sistema Operacional
* Docker
* Docker Compose
* Proxy Reverso
* Firewall
* Certificados SSL
* Rede
* Armazenamento
* Backups

Esta camada fornece toda a infraestrutura necessária para execução dos serviços.

---

## Operations

Responsável pela administração e observabilidade da plataforma.

Inclui ferramentas como:

* Portainer
* Cockpit
* Uptime Kuma
* Grafana
* Prometheus
* Logs
* Métricas
* Alertas

Esta camada não executa aplicações de negócio.

Sua função é operar e monitorar a plataforma.

---

## Services

Responsável pelos serviços compartilhados.

Exemplos:

* APIs
* Bancos de Dados
* Redis
* Serviços Python
* Serviços Java
* Autenticação
* Cache
* Mensageria

Esses componentes podem ser utilizados simultaneamente por diversas aplicações.

---

## Applications

Camada responsável pelos sistemas disponibilizados aos usuários.

Atualmente fazem parte desta camada:

* Portal
* Album Admin
* Album Mobile
* BioQuest
* Financeiro
* Sistema de Chamados (em desenvolvimento)

Novas aplicações deverão seguir os padrões definidos pela plataforma.

---

# Visão Geral da Arquitetura

```text
                                     Usuários
                                         │
                                         ▼
                              www.deja.com.br
                                         │
                                         ▼
                              app.deja.com.br
                                         │
                                         ▼
                             Reverse Proxy (NGINX)
                                         │
      ┌──────────────────────────────────┼──────────────────────────────────┐
      │                                  │                                  │
      ▼                                  ▼                                  ▼
Applications                        Services                         Operations
      │                                  │                                  │
      │                                  │                                  │
Portal                         APIs Python                      Portainer
Album                          MariaDB                          Cockpit
BioQuest                       Redis                            Uptime Kuma
Financeiro                     FastAPI                          Grafana
Chamados                                                        Prometheus
      │
      ▼
Infrastructure
      │
Ubuntu Server
Docker
Docker Compose
Firewall
SSL
Storage
Backup
```

---

# Nós da Plataforma

A plataforma poderá ser composta por um ou mais nós (Nodes).

Cada nó possui responsabilidades específicas.

Atualmente existe:

| Node    | Função      | Status   |
| ------- | ----------- | -------- |
| Node 01 | VPS Contabo | Produção |

Novos nós poderão ser incorporados futuramente, mantendo a mesma arquitetura.

---

# Princípios da Plataforma

Toda evolução deverá respeitar os seguintes princípios:

* Separação de responsabilidades.
* Documentação obrigatória.
* Versionamento em Git.
* Infraestrutura reproduzível.
* Segurança por padrão.
* Automação sempre que possível.
* Baixo acoplamento entre aplicações.
* Alta organização estrutural.
* Evolução incremental.

---

# Fluxo de Evolução

Toda alteração permanente deverá seguir o seguinte fluxo:

```text
Planejamento
      │
      ▼
Arquitetura
      │
      ▼
Implementação
      │
      ▼
Testes
      │
      ▼
Documentação
      │
      ▼
Versionamento (Git)
      │
      ▼
Produção
```

Nenhuma alteração será considerada concluída antes de percorrer todas essas etapas.
