# Publicacao na Contabo — Deja Platform e VIVARO

## Objetivo

Procedimento operacional para publicar alteracoes da API Deja Platform
e do VIVARO PWA no servidor Contabo.

Baseado na publicacao realizada e homologada em 20/11/2026.

Este documento complementa:
- docs/operations/deployment-flow.md
- docs/operations/backup-strategy.md
- docs/operations/disaster-recovery.md
- docs/operations/runbook.md
- docs/adr/ADR-003-application-publication-standard.md

## Regras obrigatorias

1. Trabalhar localmente, testar e homologar antes da publicacao.
2. Nao alterar o GitHub antes da aprovacao da implementacao local.
3. Executar um comando por vez e verificar sua saida.
4. Interromper imediatamente a publicacao em caso de erro.
5. Fazer backups antes de modificar a producao.
6. Nunca incluir midias nos backups especificos desta publicacao.
7. Nunca excluir arquivos antigos sem verificar sua finalidade.
8. Nunca reiniciar a API sem testar a importacao completa do
   pacote efetivamente instalado no ambiente virtual.
9. Nao publicar o frontend enquanto a API estiver com falhas.
10. Manter o rollback disponivel ate a homologacao final.

## Ambiente confirmado em 20/11/2026

Repositorio GitHub:
DejaLazzarotto/Deja-HomeLab

Windows:
D:\ADD\Deja-HomeLab

Servidor:
deja@185.209.230.77

Hostname interno:
vmi3133572

API:
 /var/www/deja/apps/deja-platform-api

Repositorio no servidor:
 /var/www/deja/apps/deja-platform-api/source

Ambiente Python:
 /var/www/deja/apps/deja-platform-api/.venv

Servico:
 deja-platform-api.service

API interna:
 http://127.0.0.1:8010

Banco MySQL:
 deja_platform

VIVARO:
 /var/www/deja/apps/vivaro-pwa

Workspace:
 /var/www/deja/apps/deja-workspace

Endereco publico:
 https://app.deja.com.br/vivaro/

## 1. Preparacao local

Verificar a branch master e o estado do Git:

    git status --short --branch

Executar os testes aplicaveis a alteracao.

Para alteracoes na API, obrigatoriamente testar tambem
a importacao completa da aplicacao:

    python -c "from deja_platform_api.main import app; print('OK:', len(app.routes))"

Executar os testes de integracao pertinentes.

Nao considerar suficiente um teste que apenas verifica a
existencia de uma classe ou metodo.

Para o VIVARO, executar testes Angular e build de producao.

Somente apos homologacao:
- revisar git diff;
- criar commit;
- enviar com git push origin master;
- confirmar o commit remoto.

## 2. Backups antes da publicacao

Criar diretorio identificado pela data e pelo commit:

    /var/www/deja/backups/pre-vivaro-<data>-<commit>/

Backups utilizados em 20/11/2026:

API:
- .env
- source
- scripts
- models

Banco:
- mysqldump de deja_platform com --single-transaction,
  --quick, --routines, --triggers, --events e --no-tablespaces.

Workspace:
- /var/www/deja/apps/deja-workspace

VIVARO:
- /var/www/deja/apps/vivaro-pwa

Verificar os arquivos compactados com tar -tzf
e o dump SQL compactado com gzip -t.

IMPORTANTE — EXCLUSOES DESTA OPERACAO:

Nao incluir:
- /var/www/deja/apps/deja-platform-api/uploads
- /var/www/deja/storage
- fotografias, videos e outros arquivos de midia.

Nao apagar, mover ou modificar esses diretorios.

Este backup especifico de publicacao NAO substitui a
estrategia geral de protecao dos dados persistentes
descrita em backup-strategy.md.

O arquivo .env contem dados sensiveis. Proteger acesso
aos backups e nunca enviar essas configuracoes ao Git.

## 3. Atualizacao da API

Confirmar inicialmente:

    systemctl status deja-platform-api.service --no-pager -l

Verificar o repositorio de producao:

    git -C /var/www/deja/apps/deja-platform-api/source status -sb

Confirmar o commit esperado no GitHub.

Atualizar o codigo somente se estiver limpo:

    git -C /var/www/deja/apps/deja-platform-api/source pull --ff-only origin master

Instalar o pacote utilizando o ambiente existente:

    /var/www/deja/apps/deja-platform-api/.venv/bin/python -m pip install --no-deps --no-build-isolation /var/www/deja/apps/deja-platform-api/source/deja-platform-api

## 4. BLOQUEIO OBRIGATORIO ANTES DO REINICIO

Apos instalar e ANTES de reiniciar, executar:

    /var/www/deja/apps/deja-platform-api/.venv/bin/python -c "from deja_platform_api.main import app; print('OK: API importada. Rotas:', len(app.routes))"

Se houver Traceback ou erro, NAO REINICIAR.

Investigar a falha, corrigir o codigo-fonte, testar
localmente e preparar nova versao.

Confirmar tambem que as rotas esperadas foram registradas,
considerando as configuracoes especificas do ambiente.

Observacao: o resultado de importacao isolada nao garante
que todos os endpoints funcionem. A verificacao HTTP e
funcional continua obrigatoria apos o reinicio.

Somente depois das validacoes:

    sudo systemctl restart deja-platform-api.service

Verificar:

    systemctl is-active deja-platform-api.service

    sudo journalctl -u deja-platform-api.service -n 100 --no-pager -l

    curl -sS -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:8010/health

Exigir HTTP 200 e ausencia de falhas criticas.

Nao avancar para o frontend se houver problemas.

## 5. Incidente de 20/11/2026

A API falhou apos a instalacao do commit 217cd06.

Causa:

Dentro de FotosPersonService havia um metodo chamado list.
Uma anotacao posterior usava list[tuple[...]], causando:

    TypeError: 'function' object is not subscriptable

Correcao definitiva:

    from __future__ import annotations

Inserida em:
deja-platform-api/src/deja_platform_api/fotos/people/service.py

Commit corretivo:
55ee97b

Licao:
Os testes isolados de People passaram, mas nao detectaram
a falha na importacao completa do aplicativo.

A partir deste incidente, a importacao completa do pacote
instalado e obrigatoria antes do reinicio em producao.

Nao usar edicao direta de site-packages como procedimento
normal de publicacao. A correcao emergencial realizada
nesse incidente deve permanecer registrada como excecao.

## 6. Build do VIVARO

No Windows, dentro de workspace:

    npx ng build deja-fotos-pwa --configuration production --base-href /vivaro/

Arquivos gerados em:

    workspace/dist/deja-fotos-pwa/browser

Conferir:
- index.html
- manifest.webmanifest
- ngsw.json
- ngsw-worker.js
- <base href="/vivaro/">

Criar pacote tar.gz somente com o conteudo de browser.
Testar a leitura integral do pacote antes da transferencia.

## 7. Transferencia e publicacao do frontend

Transferir via scp para /home/deja.

Validar o tar.gz recebido com tar -tzf.

Extrair a nova versao em diretorio de preparacao separado.

Validar index.html, manifesto, ngsw.json e base href.

Somente depois:
- confirmar que o backup anterior existe;
- preservar o diretorio vivaro-pwa atual com nome de rollback;
- colocar a nova versao em /var/www/deja/apps/vivaro-pwa;
- conferir permissoes e leitura pelo Nginx.

Em 20/11/2026, a troca foi feita por renomeacao dos
diretorios, com a versao anterior preservada.

Evitar modificacoes no Workspace, na API, no banco
e nos diretorios de midias durante essa etapa.

## 8. Homologacao em producao

Exigir HTTP 200:

    https://app.deja.com.br/vivaro/

Verificar tambem:
- /vivaro/manifest.webmanifest
- /vivaro/ngsw.json
- /vivaro/ngsw-worker.js

Verificar o estado e o endpoint /health da API.

Homologar no navegador:
- autenticacao;
- visualizacao de fotografias;
- navegacao entre pessoas, anos e meses;
- carregamento incremental;
- visualizador e favoritos;
- atualizacao do Service Worker.

Considerar concluido somente apos aprovacao funcional.

## 9. Recuperacao e rollback

Na falha da API:
1. Interromper a publicacao.
2. Consultar journalctl.
3. Utilizar o backup anterior e os procedimentos
   de disaster-recovery.md e runbook.md.
4. Validar importacao ANTES do reinicio.
5. Verificar /health depois da recuperacao.

Na falha do VIVARO:
1. Preservar a versao com problema para diagnostico.
2. Restaurar a pasta anterior de rollback ou o
   arquivo vivaro-pwa.tar.gz de backup.
3. Validar HTTPS e funcionamento no navegador.

Nao restaurar automaticamente o banco de dados.
Avaliar primeiro se houve alguma alteracao de schema
ou de dados e o impacto sobre registros recentes.

Nao modificar os diretorios de midias no rollback
de codigo.

## 10. Limpeza posterior

Diretorios antigos e temporarios so podem ser removidos
apos:
- homologacao em producao;
- identificacao do seu conteudo;
- confirmacao de que nao sao utilizados;
- confirmacao de backups e rollback suficientes;
- autorizacao expressa.

Nunca executar limpeza generica em /var/www/deja.

## 11. Registro da publicacao

Anotar em cada release:
- data;
- commit;
- componentes atualizados;
- resultados dos testes;
- local dos backups;
- verificacoes HTTP;
- resultado da homologacao;
- incidentes e correcoes aplicadas.

Referencia da publicacao de 20/11/2026:

Funcionalidade:
VIVARO — Pessoas organizadas por ano e mes.

Commit funcional:
217cd06

Commit corretivo:
55ee97b

Backup de producao:
pre-vivaro-people-20261120-217cd06

Resultado:
API e VIVARO homologados em producao.