# Catálogo de Aplicações — Deja Platform

## Objetivo

Este documento mantém o inventário oficial das aplicações hospedadas na Deja Platform.

Seu objetivo é facilitar a administração, documentação e evolução da plataforma.

---

# Aplicações

## Portal

| Campo   | Valor                       |
| ------- | --------------------------- |
| Nome    | Portal                      |
| Tipo    | SPA                         |
| Caminho | `/var/www/deja/apps/portal` |
| Domínio | `app.deja.com.br`           |
| Status  | Produção                    |

---

## BioQuest PWA

| Campo   | Valor                             |
| ------- | --------------------------------- |
| Nome    | BioQuest PWA                      |
| Tipo    | Progressive Web App               |
| Caminho | `/var/www/deja/apps/bioquest-pwa` |
| URL     | `/bioquest-pwa`                   |
| Status  | Desenvolvimento                   |

---

## Financeiro PWA

| Campo   | Valor                               |
| ------- | ----------------------------------- |
| Nome    | Financeiro PWA                      |
| Tipo    | Progressive Web App                 |
| Caminho | `/var/www/deja/apps/financeiro-pwa` |
| URL     | `/financeiro-pwa`                   |
| Status  | Produção                            |

---

## Backend Album

| Campo    | Valor                              |
| -------- | ---------------------------------- |
| Nome     | Backend Album                      |
| Tipo     | API Python                         |
| Caminho  | `/var/www/deja/apps/backend-album` |
| Execução | Gunicorn                           |
| Porta    | 8000                               |
| Status   | Produção                           |

---

## Album Admin

| Campo   | Valor                            |
| ------- | -------------------------------- |
| Nome    | Album Admin                      |
| Tipo    | SPA                              |
| Caminho | `/var/www/deja/apps/album-admin` |
| URL     | `/album-admin`                   |
| Status  | Produção                         |

---

## Album Mobile

| Campo   | Valor                             |
| ------- | --------------------------------- |
| Nome    | Album Mobile                      |
| Tipo    | PWA                               |
| Caminho | `/var/www/deja/apps/album-mobile` |
| URL     | `/album-mobile`                   |
| Status  | Produção                          |

---

## API Backup

| Campo      | Valor                  |
| ---------- | ---------------------- |
| Nome       | API Backup             |
| Tipo       | FastAPI                |
| Porta      | 8001                   |
| Publicação | `/api-backup`          |
| Status     | Conforme serviço ativo |

---

# Estrutura padrão

Toda nova aplicação deverá possuir:

* documentação própria;
* inventário;
* estratégia de deploy;
* definição de dependências;
* responsável técnico;
* versionamento Git.

---

# Convenções

As aplicações devem ser armazenadas em:

```text
/var/www/deja/apps
```

Aplicações de infraestrutura (como bancos de dados, filas, monitoramento ou autenticação) poderão futuramente ser movidas para uma estrutura dedicada de serviços, quando houver justificativa arquitetural.
