# Orion

> **Platform Node** da Deja Platform hospedado na infraestrutura da Contabo.

---

# Objetivo

O Orion é o primeiro nó da Deja Platform.

Sua principal responsabilidade é hospedar aplicações web, serviços de backend e componentes de infraestrutura utilizados pelos projetos desenvolvidos por Dejair Lazzarotto.

Atualmente este nó representa o ambiente oficial de produção da plataforma.

---

# Identificação

| Item                | Valor                     |
| ------------------- | ------------------------- |
| Nome                | Orion                     |
| Plataforma          | Deja Platform             |
| Tipo                | Platform Node             |
| Ambiente            | Produção                  |
| Provedor            | Contabo                   |
| Virtualização       | KVM                       |
| Sistema Operacional | Ubuntu Server 24.04.4 LTS |
| Arquitetura         | x86_64                    |
| Hostname            | vmi3133572                |

---

# Capacidade

## Processador

| Item    | Valor              |
| ------- | ------------------ |
| CPU     | AMD EPYC Processor |
| vCPUs   | 6                  |
| Núcleos | 6                  |
| Threads | 6                  |

## Memória

| Item | Valor           |
| ---- | --------------- |
| RAM  | 11 GiB          |
| Swap | Não configurada |

## Armazenamento

| Item            | Valor  |
| --------------- | ------ |
| Disco Principal | 193 GB |
| Utilizado       | 40 GB  |
| Livre           | 154 GB |

---

# Papel na Plataforma

O Orion é responsável pela execução dos componentes de produção da Deja Platform.

Entre suas responsabilidades estão:

* Hospedagem das aplicações web.
* Execução dos serviços de backend.
* Publicação dos sites.
* Execução do proxy reverso.
* Armazenamento dos projetos publicados.
* Disponibilização dos serviços aos usuários da Internet.

---

# Workspace

Todas as aplicações hospedadas encontram-se centralizadas em:

```text
/var/www/deja
```

Estrutura principal:

```text
/var/www/deja
│
├── apps
├── public
└── storage
```

---

# Aplicações Hospedadas

Atualmente o Orion hospeda:

| Aplicação           | Status                                    |
| ------------------- | ----------------------------------------- |
| Portal              | Produção                                  |
| Album Admin         | Produção                                  |
| Album Mobile        | Produção                                  |
| Backend Album       | Produção                                  |
| BioQuest            | Produção                                  |
| Financeiro PWA      | Desenvolvimento                           |
| Sistema de Chamados | Desenvolvimento local (publicação futura) |

---

# Arquitetura Atual

Atualmente o backend da aplicação Álbum encontra-se localizado dentro do diretório de aplicações.

Essa organização foi mantida por questões de compatibilidade.

Uma futura evolução da plataforma prevê a separação entre aplicações e serviços.

---

# Evolução Planejada

Estrutura pretendida:

```text
/var/www/deja
│
├── apps
├── services
├── public
└── storage
```

Essa reorganização será realizada apenas quando houver necessidade técnica, evitando alterações desnecessárias em ambientes estáveis.

---

# Situação Atual

O Orion encontra-se operacional e atende às necessidades atuais da Deja Platform.

A infraestrutura apresenta disponibilidade de recursos para expansão da plataforma, permitindo a publicação de novas aplicações e serviços sem necessidade imediata de ampliação da capacidade computacional.
