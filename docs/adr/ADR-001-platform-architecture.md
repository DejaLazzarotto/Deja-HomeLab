# ADR-001 — Arquitetura da Plataforma

**Status:** Aceito

**Data:** 25/06/2026

---

# Contexto

O projeto **Deja HomeLab** tem como objetivo documentar, organizar e evoluir a infraestrutura utilizada para desenvolvimento, implantação e hospedagem das aplicações desenvolvidas por Dejair Lazzarotto.

Embora o nome do repositório seja *Deja HomeLab*, sua finalidade vai além de um laboratório de estudos. O repositório representa a documentação oficial da plataforma utilizada para hospedar aplicações, serviços e componentes de infraestrutura.

Para garantir organização, escalabilidade e facilidade de manutenção, tornou-se necessário definir uma arquitetura conceitual única que sirva como referência para toda a documentação e para futuras decisões técnicas.

---

# Problema

Sem uma arquitetura definida, a documentação tende a ser organizada por tecnologias (Docker, NGINX, Grafana etc.), dificultando a compreensão da plataforma como um todo.

Além disso, a substituição de tecnologias ao longo do tempo exigiria reorganizações frequentes da documentação.

Era necessário estabelecer uma estrutura baseada em responsabilidades, e não em ferramentas.

---

# Decisão

A plataforma será organizada em quatro camadas principais.

## 1. Desenvolvimento

Responsável pela criação e manutenção do código-fonte.

Inclui:

* Estação de trabalho Windows
* Visual Studio Code
* Git
* Projetos locais
* Testes
* Versionamento

Nenhum desenvolvimento será realizado diretamente no servidor de produção.

---

## 2. Plataforma

Responsável por fornecer toda a infraestrutura necessária para execução dos serviços.

Inclui componentes como:

* Ubuntu Server
* Docker
* Docker Compose
* Proxy Reverso
* Firewall
* Certificados SSL
* Armazenamento
* Backups
* Monitoramento
* Logs

Esta camada não contém regras de negócio das aplicações.

---

## 3. Serviços

Responsável pelos componentes compartilhados entre aplicações.

Exemplos:

* APIs
* Bancos de Dados
* Cache
* Serviços de autenticação
* Serviços de mensageria
* Outros componentes reutilizáveis

Os serviços devem ser independentes das aplicações consumidoras.

---

## 4. Aplicações

Responsável pelos sistemas disponibilizados aos usuários.

Atualmente fazem parte desta camada:

* Portal
* Álbum Admin
* Álbum Mobile
* BioQuest
* Financeiro
* Sistema de Chamados

Novas aplicações deverão seguir o mesmo padrão arquitetural.

---

# Princípios Arquiteturais

Toda evolução da plataforma deverá respeitar os seguintes princípios:

* Separação de responsabilidades.
* Documentação obrigatória.
* Versionamento em Git.
* Infraestrutura reproduzível.
* Padronização de nomenclatura.
* Escalabilidade.
* Segurança por padrão.
* Preferência por soluções baseadas em containers.
* Baixo acoplamento entre aplicações.

---

# Consequências

Esta decisão estabelece uma estrutura arquitetural permanente para o projeto.

Toda documentação futura deverá estar alinhada com essas quatro camadas.

Novas tecnologias poderão ser incorporadas sem alterar a arquitetura conceitual, bastando identificar em qual camada elas se encaixam.

Isso torna a documentação mais estável, facilita a manutenção e simplifica a evolução da plataforma ao longo do tempo.

---

# Situação Atual

Esta ADR é a primeira decisão formal registrada para a plataforma e servirá como base para todas as demais decisões arquiteturais.
