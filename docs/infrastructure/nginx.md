# NGINX — Edge Layer da Deja Platform

## Objetivo

O NGINX é o componente responsável pela Edge Layer da Deja Platform.

Sua função é centralizar todo o acesso externo às aplicações hospedadas no Node 01 — Orion, fornecendo um ponto único de entrada para serviços web.

---

# Responsabilidades

O NGINX é responsável por:

* Publicação de aplicações web;
* Proxy reverso para APIs e serviços internos;
* Encerramento das conexões HTTPS (TLS);
* Gerenciamento de certificados SSL;
* Redirecionamentos HTTP → HTTPS;
* Encaminhamento para aplicações internas;
* Padronização da infraestrutura web.

---

# Arquitetura

```
Internet
     │
     ▼
NGINX (80 / 443)
     │
     ├────────► Portal
     ├────────► BioQuest PWA
     ├────────► Financeiro PWA
     ├────────► Album Admin
     ├────────► Album Mobile
     ├────────► Backend Album (Gunicorn)
     ├────────► API Backup
     └────────► Webmin
```

Todo acesso público deve passar pelo NGINX.

---

# Servidor

Node:

```
Node 01 — Orion
```

Sistema Operacional:

```
Ubuntu Server 24.04 LTS
```

Versão do NGINX:

```
1.24.0
```

---

# Virtual Hosts

## deja-app

Domínio:

```
app.deja.com.br
```

Responsável por publicar:

* Portal
* BioQuest PWA
* Financeiro PWA
* Album Admin
* Album Mobile
* Backend Album
* API Backup
* phpMyAdmin

---

## webmin

Domínio:

```
webmin.deja.com.br
```

Proxy reverso para:

```
127.0.0.1:10000
```

---

# Serviços internos

| Serviço    | Porta |
| ---------- | ----: |
| Gunicorn   |  8000 |
| API Backup |  8001 |
| Webmin     | 10000 |
| MariaDB    |  3306 |

Todos os serviços internos devem permanecer acessíveis apenas localmente, sempre que possível.

---

# Certificados

Os certificados SSL são gerenciados pelo Certbot utilizando Let's Encrypt.

Os certificados ficam armazenados em:

```
/etc/letsencrypt/
```

---

# Estrutura dos Virtual Hosts

```
/etc/nginx/

├── nginx.conf
├── sites-available/
└── sites-enabled/
```

Cada domínio deve possuir seu próprio arquivo de configuração.

---

# Convenções

Cada aplicação deverá possuir:

* domínio ou subdomínio próprio;
* configuração isolada;
* proxy reverso independente;
* documentação correspondente.

Não utilizar um único Virtual Host para acumular aplicações indefinidamente.

---

# Diretrizes da Plataforma

Toda nova aplicação deverá:

1. possuir documentação;
2. possuir inventário;
3. possuir estratégia de deploy;
4. possuir Virtual Host próprio quando justificar;
5. utilizar HTTPS obrigatoriamente.

---

# Evoluções Futuras

Entre as melhorias previstas para a Edge Layer estão:

* separação gradual do arquivo `deja-app`;
* organização por domínio;
* templates reutilizáveis para novos Virtual Hosts;
* padronização de logs;
* política de cache;
* compressão (gzip/Brotli);
* cabeçalhos de segurança;
* monitoramento e métricas;
* backup automatizado das configurações do NGINX.

Essas evoluções deverão ocorrer de forma incremental, preservando a estabilidade da plataforma.
