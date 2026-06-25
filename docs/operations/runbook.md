# Runbook Operacional — Deja Platform

## Objetivo

Este documento descreve os procedimentos operacionais padrão da Deja Platform.

Seu objetivo é garantir que a administração da plataforma seja previsível, reproduzível e independente do conhecimento tácito do administrador.

---

# Plataforma

Nome:

```text
Deja Platform
```

Servidor principal:

```text
Node 01 — Orion
```

Sistema Operacional:

```text
Ubuntu Server 24.04 LTS
```

---

# Princípios Operacionais

Toda intervenção na plataforma deve priorizar:

* disponibilidade;
* segurança;
* simplicidade;
* rastreabilidade;
* documentação.

Alterações estruturais devem ser precedidas por uma ADR.

---

# Ordem de Diagnóstico

Ao investigar um problema, seguir a seguinte sequência:

1. Verificar conectividade do servidor.
2. Verificar utilização de CPU, memória e disco.
3. Verificar status dos serviços.
4. Verificar logs.
5. Verificar NGINX.
6. Verificar aplicação.
7. Verificar banco de dados.
8. Validar funcionamento externo.

---

# Verificações Básicas

## Espaço em disco

```bash
df -h
```

---

## Memória

```bash
free -h
```

---

## Processos

```bash
top
```

ou

```bash
htop
```

---

## Serviços

```bash
systemctl status nome-do-servico
```

---

## NGINX

Validar configuração:

```bash
sudo nginx -t
```

Recarregar configuração:

```bash
sudo systemctl reload nginx
```

Reiniciar:

```bash
sudo systemctl restart nginx
```

---

# SSL

Renovar certificados:

```bash
sudo certbot renew
```

Testar renovação:

```bash
sudo certbot renew --dry-run
```

---

# Logs

Sempre consultar os logs antes de reiniciar um serviço.

Exemplos:

```bash
journalctl -u nginx
```

```bash
journalctl -u nome-do-servico
```

---

# Deploy

Antes do deploy:

* validar build;
* validar documentação;
* realizar backup quando necessário.

Após o deploy:

* validar aplicação;
* validar HTTPS;
* validar logs;
* validar APIs.

---

# Backup

Antes de alterações estruturais:

* backup das configurações;
* backup da aplicação;
* backup do banco de dados (quando aplicável).

---

# Rollback

Em caso de falha:

1. Restaurar configuração anterior.
2. Restaurar aplicação anterior.
3. Validar funcionamento.
4. Registrar ocorrência.

---

# Boas Práticas

Nunca editar diretamente um ambiente de produção sem backup.

Nunca alterar múltiplos componentes simultaneamente.

Sempre validar as alterações antes de concluir uma intervenção.

Toda mudança relevante deve ser registrada no repositório Git.

---

# Evolução

Este Runbook deverá ser atualizado continuamente conforme novos serviços e procedimentos forem incorporados à Deja Platform.
