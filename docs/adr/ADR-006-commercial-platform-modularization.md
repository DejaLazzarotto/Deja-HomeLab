# ADR-006 — Modularização da Plataforma Comercial

## Status

Accepted

## Data

25 de agosto de 2026

## Contexto

A Deja Platform foi concebida como uma plataforma modular, orientada por contratos estáveis, capaz de hospedar e integrar diferentes produtos sem incorporar suas regras de negócio ao Kernel.

A implementação atual evoluiu inicialmente a partir do produto Deja Indicadores. Como consequência, algumas capacidades institucionais reutilizáveis foram implementadas dentro de diretórios, pacotes e namespaces identificados como `deja-indicadores`.

Entre essas capacidades encontram-se:

* autenticação;
* autorização;
* sessão;
* gerenciamento de usuários;
* gerenciamento de organizações;
* gerenciamento de tenants e ambientes;
* gerenciamento e liberação de módulos;
* guards compartilhados;
* composição e navegação do Workspace;
* API central.

Com a incorporação do Deja Chamados e o planejamento do Deja Fotos, essa organização passou a produzir acoplamento incorreto entre a plataforma e o primeiro produto criado sobre ela.

Também existe uma inconsistência no catálogo comercial atual. As chaves `indicators`, `measurements` e `reports` representam funcionalidades internas do Deja Indicadores, enquanto `chamados` representa um produto comercial completo.

A reconstrução do Álbum de Fotos exige que essa separação seja corrigida antes da incorporação de um terceiro produto.

## Decisão

A Deja Platform será consolidada como a plataforma comercial multi-organização responsável pelas capacidades institucionais compartilhadas.

Os produtos Deja Indicadores, Deja Chamados e Deja Fotos serão módulos comerciais irmãos, construídos sobre os contratos disponibilizados pela plataforma.

A implementação continuará inicialmente como um monólito modular, com frontend central e API central. A divisão em serviços independentes somente será considerada quando houver justificativa técnica comprovada.

## Identidade dos componentes

A identidade técnica e comercial será organizada da seguinte forma:

| Componente        | Responsabilidade                                      |
| ----------------- | ----------------------------------------------------- |
| Deja Platform     | Plataforma institucional e comercial                  |
| Deja Workspace    | Interface web central da plataforma                   |
| Deja Platform API | Backend central e monólito modular                    |
| Deja Indicadores  | Produto de indicadores e gestão                       |
| Deja Chamados     | Produto de atendimento e chamados                     |
| Deja Fotos        | Produto de fotos, vídeos, álbuns, pessoas e curadoria |

O frontend Angular continuará tecnicamente identificado como `deja-workspace`.

O backend atualmente identificado como `deja-indicadores-api` deverá ser migrado, de forma controlada, para `deja-platform-api`.

O pacote Python atualmente identificado como `deja_indicadores_api` deverá ser migrado para `deja_platform_api`.

A documentação específica existente em `docs/products/deja-indicadores` continuará pertencendo ao produto Deja Indicadores e não será renomeada como documentação da plataforma.

## Responsabilidades da Deja Platform

Pertencem ao núcleo institucional compartilhado:

* autenticação;
* autorização;
* gerenciamento de sessão;
* organizações;
* tenants;
* ambientes;
* usuários;
* papéis;
* permissões;
* catálogo comercial de módulos;
* liberação de módulos por organização;
* auditoria institucional;
* contratos compartilhados;
* Workspace SDK;
* shell, navegação e identidade visual;
* infraestrutura de widgets e dashboards;
* configuração institucional;
* observabilidade;
* tratamento padronizado de erros;
* contratos compartilhados de armazenamento e processamento assíncrono.

O Kernel não implementará regras específicas de Indicadores, Chamados ou Fotos.

## Responsabilidades do Deja Indicadores

Permanecem no produto Deja Indicadores:

* empresas;
* indicadores;
* medições;
* metas;
* dashboards especializados;
* relatórios gerenciais;
* diagnósticos;
* recomendações;
* planos de ação;
* metodologia de gestão;
* demais regras específicas do produto.

## Responsabilidades do Deja Chamados

Pertencem ao produto Deja Chamados:

* clientes atendidos;
* chamados;
* filas;
* categorias;
* prioridades;
* técnicos;
* comentários;
* anexos;
* histórico de atendimento;
* portal de atendimento;
* demais regras específicas de suporte técnico.

## Responsabilidades do Deja Fotos

Pertencem ao produto Deja Fotos:

* mídias;
* álbuns;
* descrições;
* pessoas;
* assinaturas faciais;
* ocorrências faciais;
* curadoria;
* visualizações;
* compartilhamentos;
* processamento de imagens e vídeos;
* reconhecimento e identificação facial;
* experiência administrativa integrada ao Workspace;
* PWA independente para visualização.

Os nomes `Album Admin`, `Album Mobile` e `Backend Album` serão considerados identificadores do sistema legado.

A nova experiência administrativa será um módulo do Deja Workspace. A experiência móvel será publicada como PWA independente do Deja Fotos, utilizando a mesma autenticação, API e domínio de dados.

## Catálogo comercial

O catálogo comercial deverá representar produtos contratáveis, e não funcionalidades internas.

As chaves comerciais oficiais serão:

| Chave         | Produto          |
| ------------- | ---------------- |
| `indicadores` | Deja Indicadores |
| `chamados`    | Deja Chamados    |
| `fotos`       | Deja Fotos       |

Somente o `platform_admin` poderá liberar ou bloquear módulos para uma organização.

O cliente não poderá contratar, liberar, desbloquear ou alterar módulos por conta própria.

As funcionalidades internas de cada produto serão controladas por papéis, permissões e capacidades do próprio módulo.

As chaves existentes `indicators`, `measurements` e `reports` deverão passar por uma transição compatível. Elas não serão removidas abruptamente.

Organizações existentes que possuam qualquer uma dessas liberações deverão preservar o acesso ao Deja Indicadores durante a consolidação.

## Registro de módulos

Cada produto deverá registrar seus próprios recursos por contratos institucionais.

O núcleo registrará somente recursos compartilhados.

Cada módulo será responsável pelo registro de:

* rotas;
* widgets;
* dashboards;
* itens de navegação;
* comandos;
* permissões;
* capacidades;
* dependências;
* metadados;
* contratos de API.

Widgets e dashboards específicos não deverão ser registrados como pertencentes ao núcleo.

O Workspace deverá apresentar somente os módulos liberados para a organização e permitidos ao usuário autenticado.

## Estratégia de mídia do Deja Fotos

A partir da nova versão, todos os uploads passarão por validação e padronização.

O arquivo original recebido será preservado de forma imutável para:

* auditoria;
* rastreabilidade;
* reprocessamento;
* recuperação;
* investigação de falhas;
* preservação de metadados.

A padronização não sobrescreverá o arquivo original.

O sistema produzirá derivados canônicos para uso interno e exibição.

### Fotografias

* fotografias sem transparência serão normalizadas para JPEG;
* imagens com transparência serão normalizadas para PNG;
* versões otimizadas de exibição e miniaturas poderão utilizar WebP;
* orientação, dimensões, perfil de cor e metadados relevantes serão tratados de forma explícita;
* a data original será extraída antes da conversão;
* formatos como BMP, TIFF, HEIC e outros formatos aceitos serão convertidos para o padrão adequado;
* arquivos inválidos ou incompatíveis serão colocados em quarentena.

### Vídeos

O formato canônico de reprodução será:

* contêiner MP4;
* vídeo H.264;
* áudio AAC;
* metadados compatíveis com reprodução progressiva pela web.

MP4 foi escolhido em lugar de MKV por possuir maior compatibilidade com navegadores, celulares, computadores e PWAs.

Arquivos MOV, MPG, MKV e outros formatos aceitos serão convertidos para o formato canônico.

### Processamento

O processamento de mídia será assíncrono e não ocorrerá dentro da requisição de upload.

Cada mídia possuirá um estado explícito, incluindo:

* recebido;
* validando;
* processando;
* pronto;
* falhou;
* quarentena.

O sistema deverá validar:

* extensão declarada;
* tipo MIME;
* assinatura real do arquivo;
* tamanho;
* integridade;
* dimensões;
* duração;
* codecs;
* checksum;
* metadados relevantes.

Falhas nunca serão ignoradas silenciosamente.

## Armazenamento

Novos uploads serão armazenados de forma isolada por organização.

Os caminhos físicos não dependerão diretamente do nome original informado pelo usuário.

O banco manterá a relação entre:

* organização;
* mídia;
* arquivo original;
* derivados;
* checksum;
* formato;
* tamanho;
* estado de processamento;
* metadados;
* auditoria.

O diretório legado `/var/www/deja/storage/midias` permanecerá imutável durante a reconstrução.

Nenhum arquivo legado será apagado, movido, renomeado, sobrescrito ou reorganizado.

## Banco de dados

O banco legado `deja_album` permanecerá preservado como fonte de migração e referência até a validação completa da nova versão.

O Deja Fotos utilizará um novo modelo relacional, separado do banco legado.

A decisão sobre o nome físico definitivo do banco central da plataforma será tratada separadamente, pois envolve implantação, credenciais, backups, Alembic e ambientes existentes.

A nova modelagem deverá separar explicitamente:

* pessoa;
* assinatura facial;
* detecção facial;
* ocorrência facial;
* mídia;
* arquivo original;
* derivado;
* álbum;
* descrição;
* processamento;
* auditoria.

Dados inválidos não serão descartados. Eles serão identificados, preservados e encaminhados para quarentena ou revisão.

## Migração do sistema legado

A importação será realizada por uma ferramenta temporária, idempotente e reiniciável.

A ferramenta lerá simultaneamente:

* o banco legado `deja_album`;
* o diretório legado `/var/www/deja/storage/midias`.

A ferramenta deverá:

* iniciar em modo de simulação;
* não alterar o banco legado;
* não alterar os arquivos legados;
* calcular checksums;
* validar integridade;
* reconciliar banco e armazenamento;
* identificar registros sem arquivo;
* identificar arquivos sem registro;
* identificar os 24 arquivos inicialmente divergentes;
* importar dados válidos;
* separar pessoas, assinaturas e ocorrências;
* colocar dados inválidos em quarentena;
* produzir relatório detalhado;
* continuar após interrupções;
* impedir duplicações;
* permitir repetição segura;
* atribuir todos os dados legados a uma organização explicitamente definida.

Nenhuma informação será corrigida ou descartada silenciosamente.

## Estratégia de transição

A transição será incremental e dividida em etapas.

### Etapa 1 — Documentação

* registrar esta decisão;
* mapear o estado atual;
* definir contratos;
* definir requisitos;
* definir o modelo de dados;
* definir o plano de migração;
* aprovar a arquitetura antes da implementação.

### Etapa 2 — Identidade da plataforma

* substituir a identidade pública `Deja Indicadores` por `Deja Platform` no shell compartilhado;
* preservar a identidade Deja Indicadores dentro do módulo;
* planejar a renomeação técnica da API;
* não alterar contratos HTTP simultaneamente.

### Etapa 3 — Extração das capacidades compartilhadas

* mover autenticação para o núcleo da plataforma;
* mover gerenciamento de usuários para o núcleo;
* mover gerenciamento de organizações, tenants e ambientes para o núcleo;
* mover gerenciamento de módulos para o núcleo;
* atualizar imports de forma controlada;
* manter testes aprovados durante toda a transição.

### Etapa 4 — Registro modular

* criar contratos de registro para rotas, widgets, dashboards e navegação;
* fazer o Deja Indicadores registrar seus recursos;
* conectar o Deja Chamados ao Workspace;
* preparar o ponto de extensão do Deja Fotos;
* impedir dependências diretas entre produtos.

### Etapa 5 — Consolidação do catálogo comercial

* criar a chave comercial `indicadores`;
* preservar o acesso das organizações existentes;
* manter compatibilidade temporária com as chaves atuais;
* migrar guards e verificações;
* validar rollback;
* somente depois descontinuar as chaves antigas.

### Etapa 6 — Deja Fotos

* registrar o módulo comercial sem liberá-lo automaticamente;
* criar o domínio de mídia;
* criar armazenamento isolado;
* criar processamento assíncrono;
* criar experiência administrativa;
* criar PWA de visualização;
* criar ferramenta de importação;
* validar dados legados antes da ativação.

## Compatibilidade

A renomeação técnica do backend não deverá alterar simultaneamente:

* URLs públicas;
* contratos JSON;
* histórico de migrations;
* identificadores persistidos;
* dados existentes;
* permissões existentes.

O prefixo HTTP atual será preservado durante a primeira etapa da renomeação.

O versionamento `/api/v1` será tratado em decisão e transição próprias, com período de compatibilidade quando necessário.

As migrations já executadas não serão reescritas.

## Segurança

Toda evolução deverá aplicar:

* isolamento por organização;
* menor privilégio;
* autenticação central;
* autorização no backend;
* validação de propriedade dos recursos;
* auditoria;
* proteção contra enumeração;
* validação de uploads;
* limites de tamanho;
* proteção contra conteúdo malicioso;
* credenciais fora do código;
* operações transacionais;
* tratamento explícito de falhas.

A interface nunca será considerada fonte confiável para decisões de autorização.

## Consequências

### Benefícios

* identidade clara da plataforma;
* produtos independentes;
* menor acoplamento;
* reutilização de capacidades;
* incorporação segura de novos módulos;
* catálogo comercial consistente;
* segurança centralizada;
* melhor testabilidade;
* evolução gradual;
* preservação do legado;
* padronização futura das mídias.

### Custos

* renomeação coordenada do backend;
* atualização de muitos imports;
* reorganização de features do frontend;
* criação de contratos de registro;
* transição das chaves comerciais existentes;
* ampliação dos testes;
* atualização de documentação e deploy;
* necessidade de processamento assíncrono e armazenamento derivado.

### Riscos

* quebra de imports durante a renomeação;
* perda de acesso por migração incorreta das chaves;
* conflito entre nomes antigos e novos;
* acoplamento indevido entre módulos;
* aumento temporário da complexidade durante a compatibilidade;
* consumo adicional de armazenamento pela preservação dos originais e derivados.

Esses riscos serão controlados por mudanças pequenas, testes completos, migrations reversíveis, documentação e validação antes de cada commit.

## Alternativas rejeitadas

### Continuar usando Deja Indicadores como nome da plataforma

Rejeitada porque transforma um produto específico na identidade de todo o ecossistema e aumenta o acoplamento.

### Criar um backend independente para cada produto imediatamente

Rejeitada nesta fase por aumentar complexidade operacional, autenticação distribuída, observabilidade, transações e manutenção sem necessidade comprovada.

### Incorporar Fotos diretamente dentro de Deja Indicadores

Rejeitada porque Fotos possui domínio, experiência e ciclo de vida próprios.

### Converter e substituir os arquivos originais

Rejeitada por eliminar rastreabilidade, reduzir a capacidade de recuperação e poder causar perda irreversível de qualidade ou metadados.

### Utilizar MKV como formato canônico de vídeo

Rejeitada pela compatibilidade inferior com navegadores e PWAs quando comparado a MP4 com H.264 e AAC.

### Manter funcionalidades internas como módulos comerciais independentes

Rejeitada porque mistura produtos contratáveis com capacidades internas e dificulta a administração comercial da plataforma.

## Fora do escopo deste ADR

Este ADR não define:

* o modelo relacional completo do Deja Fotos;
* a implementação do worker assíncrono;
* a tecnologia definitiva da fila;
* os limites definitivos de upload;
* a estratégia definitiva de CDN;
* o nome físico definitivo do banco central;
* a data de desativação do sistema legado;
* o detalhamento visual das interfaces;
* a execução imediata de migrations;
* qualquer alteração na produção.

Essas decisões serão documentadas e aprovadas separadamente.

## Critérios de aceitação arquitetural

Esta decisão será considerada atendida quando:

* a plataforma possuir identidade central própria;
* capacidades compartilhadas não estiverem dentro do módulo Indicadores;
* Indicadores, Chamados e Fotos forem módulos irmãos;
* cada produto registrar seus próprios recursos;
* somente o `platform_admin` controlar liberações comerciais;
* o catálogo representar produtos completos;
* o Deja Fotos possuir armazenamento isolado e processamento padronizado;
* o legado permanecer preservado;
* testes e documentação comprovarem a transição.
