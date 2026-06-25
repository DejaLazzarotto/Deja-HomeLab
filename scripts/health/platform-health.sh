# Platform Health Check

## Objetivo

O Health Check é o procedimento padrão para verificar a integridade operacional da Deja Platform.

Ele deverá ser executado antes de:

* deploys;
* atualizações;
* alterações estruturais;
* backups;
* intervenções de manutenção.

Também poderá ser executado periodicamente de forma automatizada.

---

# Verificações

O script deverá validar, no mínimo:

## Sistema Operacional

* uptime;
* carga do sistema;
* uso de CPU;
* memória disponível;
* espaço em disco.

---

## Rede

* conectividade externa;
* resolução DNS;
* portas principais.

---

## Serviços

Verificar:

* NGINX;
* MariaDB;
* Gunicorn;
* Webmin;
* demais serviços cadastrados.

---

## NGINX

Validar:

* configuração (`nginx -t`);
* status do serviço;
* certificados SSL.

---

## Banco de Dados

Verificar:

* disponibilidade;
* conexão local;
* processo ativo.

---

## Aplicações

Verificar:

* Portal;
* BioQuest PWA;
* Financeiro PWA;
* Album Admin;
* Album Mobile;
* APIs publicadas.

---

## Armazenamento

Verificar:

* espaço livre;
* montagem dos volumes;
* permissões básicas.

---

# Resultado

Ao final da execução, o Health Check deverá apresentar um resumo contendo:

* verificações aprovadas;
* alertas;
* falhas críticas;
* data e hora da execução.

---

# Evolução

O Health Check poderá evoluir para incluir:

* geração de relatório em JSON;
* exportação em HTML;
* integração com Telegram;
* integração com monitoramento;
* execução automática via cron ou systemd timer.

Seu objetivo é tornar-se a principal ferramenta de diagnóstico operacional da Deja Platform.
