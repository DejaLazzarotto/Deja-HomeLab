# Disaster Recovery Plan (DRP) — Deja Platform

## Objetivo

Este documento define o procedimento oficial para recuperação da Deja Platform após perda parcial ou total da infraestrutura.

Seu objetivo é reduzir o tempo de indisponibilidade e garantir uma recuperação previsível da plataforma.

---

# Escopo

Este plano contempla a recuperação do **Node 01 — Orion**, incluindo:

* Sistema Operacional;
* Configurações;
* Serviços;
* Aplicações;
* Banco de Dados;
* Certificados SSL;
* Documentação.

---

# Cenários

## Falha de aplicação

Exemplos:

* erro após deploy;
* falha em serviço específico;
* corrupção de arquivos da aplicação.

Recuperação:

* rollback da aplicação;
* validação dos logs;
* restauração de backup, quando necessário.

---

## Falha de serviço

Exemplos:

* NGINX;
* Gunicorn;
* MariaDB;
* Webmin.

Recuperação:

* validar configuração;
* restaurar configuração anterior;
* reiniciar serviço;
* validar funcionamento.

---

## Corrupção do banco

Recuperação:

* interromper gravações;
* restaurar backup válido;
* validar integridade dos dados.

---

## Perda total da VPS

Recuperação completa da infraestrutura.

---

# Ordem de Recuperação

## Etapa 1

Provisionar nova VPS.

---

## Etapa 2

Instalar:

* Ubuntu Server LTS;
* atualizações de segurança;
* acesso SSH.

---

## Etapa 3

Restaurar:

* usuários;
* chaves SSH;
* estrutura de diretórios.

---

## Etapa 4

Instalar os componentes da plataforma:

* NGINX;
* Certbot;
* MariaDB;
* Gunicorn;
* Webmin;
* dependências das aplicações.

---

## Etapa 5

Restaurar:

```text
/var/www/deja
```

---

## Etapa 6

Restaurar:

```text
/etc/nginx
```

---

## Etapa 7

Restaurar:

```text
/etc/letsencrypt
```

---

## Etapa 8

Restaurar banco de dados.

---

## Etapa 9

Inicializar serviços.

---

## Etapa 10

Validar:

* HTTPS;
* aplicações;
* APIs;
* banco;
* logs.

---

# Checklist Final

* Servidor acessível.
* SSH funcionando.
* NGINX ativo.
* HTTPS válido.
* Banco operacional.
* Aplicações respondendo.
* Logs sem erros críticos.
* Backups configurados.
* Documentação sincronizada.

---

# Objetivos Operacionais

## RTO

Tempo máximo desejado para recuperação:

```text
Até 8 horas
```

---

## RPO

Perda máxima aceitável de dados:

```text
Até 24 horas
```

Esses valores poderão ser revisados conforme a criticidade da plataforma.

---

# Evolução

Com a maturidade da Deja Platform, o plano poderá evoluir para incluir:

* servidor secundário;
* replicação de banco de dados;
* DNS com failover;
* backups externos automáticos;
* infraestrutura como código (Ansible, Terraform ou equivalente);
* recuperação automatizada.
