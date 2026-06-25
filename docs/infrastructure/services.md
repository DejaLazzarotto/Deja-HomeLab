# Catálogo de Serviços — Deja Platform

## Objetivo

Este documento mantém o inventário oficial dos serviços de infraestrutura executados na Deja Platform.

Os serviços descritos aqui fornecem suporte para a execução, publicação, administração e armazenamento das aplicações hospedadas no Node 01 — Orion.

---

# Serviços

## NGINX

| Campo         | Valor                      |
| ------------- | -------------------------- |
| Função        | Edge Layer / Proxy Reverso |
| Gerenciador   | systemd                    |
| Porta pública | 80 / 443                   |
| Status        | Produção                   |

Responsabilidades:

* Proxy reverso;
* HTTPS;
* Certificados SSL;
* Publicação de aplicações;
* Redirecionamentos.

---

## Gunicorn

| Campo     | Valor         |
| --------- | ------------- |
| Função    | Servidor WSGI |
| Porta     | 8000          |
| Exposição | Localhost     |
| Status    | Produção      |

Responsável pela execução das aplicações Python publicadas através do NGINX.

---

## API Backup

| Campo     | Valor           |
| --------- | --------------- |
| Função    | Serviço FastAPI |
| Porta     | 8001            |
| Exposição | Localhost       |
| Status    | Sob demanda     |

Disponibiliza funcionalidades relacionadas ao gerenciamento de backups da plataforma.

---

## MariaDB

| Campo     | Valor     |
| --------- | --------- |
| Porta     | 3306      |
| Exposição | Localhost |
| Status    | Produção  |

Banco de dados principal da plataforma.

---

## MySQL X Protocol

| Campo     | Valor     |
| --------- | --------- |
| Porta     | 33060     |
| Exposição | Localhost |
| Status    | Produção  |

Interface adicional disponibilizada pelo MariaDB para clientes compatíveis.

---

## Webmin

| Campo      | Valor         |
| ---------- | ------------- |
| Porta      | 10000         |
| Publicação | Proxy reverso |
| Status     | Produção      |

Ferramenta administrativa do servidor.

O acesso preferencial deve ocorrer através do domínio:

```text
https://webmin.deja.com.br
```

---

## OpenSSH

| Campo  | Valor    |
| ------ | -------- |
| Porta  | 22       |
| Status | Produção |

Serviço utilizado para administração remota do Node 01 — Orion.

---

# Gerenciamento

Todos os serviços permanentes devem possuir:

* inicialização automática;
* gerenciamento por `systemd` ou tecnologia equivalente;
* documentação;
* estratégia de recuperação.

---

# Exposição de Rede

## Serviços públicos

| Serviço | Porta |
| ------- | ----: |
| HTTP    |    80 |
| HTTPS   |   443 |
| SSH     |    22 |

---

## Serviços internos

| Serviço    | Porta |
| ---------- | ----: |
| Gunicorn   |  8000 |
| API Backup |  8001 |
| MariaDB    |  3306 |
| MySQL X    | 33060 |

Sempre que possível, os serviços internos deverão permanecer acessíveis apenas via `localhost`.

---

# Evolução

À medida que novos componentes forem incorporados (Docker, Redis, Prometheus, Grafana, MinIO, filas, autenticação centralizada etc.), este catálogo deverá ser atualizado.

A documentação deve refletir o estado real da infraestrutura em produção.
