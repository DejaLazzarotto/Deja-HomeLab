# Estratégia de Backup — Deja Platform

## Objetivo

Este documento define a estratégia oficial de backup da Deja Platform.

Seu objetivo é minimizar a perda de dados, reduzir o tempo de recuperação e garantir a continuidade operacional em caso de falhas.

---

# Princípios

A estratégia de backup deve seguir os princípios:

* simplicidade;
* automação sempre que possível;
* restauração validada;
* versionamento;
* documentação.

Um backup só é considerado válido quando sua restauração é possível.

---

# Escopo

Os seguintes componentes devem ser protegidos:

## Infraestrutura

* Configurações do NGINX;
* Configurações do systemd;
* Scripts operacionais;
* Configurações do servidor.

---

## Aplicações

Diretório:

```text
/var/www/deja/apps
```

---

## Dados Persistentes

Diretório:

```text
/var/www/deja/storage
```

---

## Banco de Dados

MariaDB

Método:

* Dump lógico (`mysqldump`);
* Quando necessário, backup físico.

---

## Certificados

Diretório:

```text
/etc/letsencrypt
```

---

# Frequência

| Componente             | Frequência                 |
| ---------------------- | -------------------------- |
| Banco de dados         | Diária                     |
| Aplicações             | Diária                     |
| Storage                | Diária                     |
| Configurações do NGINX | Sempre antes de alterações |
| Certificados           | Semanal                    |
| Documentação           | Versionada em Git          |

---

# Antes de Alterações

Antes de qualquer alteração estrutural devem ser realizados:

* backup das configurações;
* backup da aplicação afetada;
* backup do banco de dados (quando houver alteração de schema ou dados críticos).

---

# Retenção

A política inicial será:

| Tipo    |  Retenção |
| ------- | --------: |
| Diário  |    7 dias |
| Semanal | 4 semanas |
| Mensal  |  12 meses |

Essa política poderá ser revisada conforme o crescimento da plataforma.

---

# Localização

Os backups poderão ser armazenados em:

* armazenamento local;
* servidor secundário;
* armazenamento em nuvem.

A estratégia poderá evoluir para múltiplas cópias em locais distintos.

---

# Restauração

Toda restauração deverá seguir a seguinte ordem:

1. Infraestrutura;
2. Configurações;
3. Banco de dados;
4. Aplicações;
5. Dados persistentes;
6. Validação funcional.

---

# Testes

Periodicamente deverão ser realizados testes de restauração para garantir a integridade dos backups.

---

# Evolução

Como evolução da plataforma, poderão ser incorporados:

* backups automatizados;
* criptografia dos backups;
* armazenamento externo;
* notificações de sucesso ou falha;
* verificação automática de integridade.

Essas melhorias deverão preservar os princípios de simplicidade, confiabilidade e recuperação rápida.
