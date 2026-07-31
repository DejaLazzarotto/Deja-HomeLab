# 03. Organização

## Objetivo

Esta seção define a organização arquitetural do Data Store, identificando seus principais componentes, responsabilidades e relacionamentos dentro do ecossistema da Deja Indicadores.

A organização apresentada é lógica e institucional, permanecendo independente das tecnologias de persistência utilizadas na implementação.

---

# Visão Arquitetural

O Data Store é organizado em camadas de responsabilidade claramente separadas.

Sua arquitetura pode ser representada da seguinte forma:

```
                Data Pipeline
                     │
                     ▼
              Persistência Pública
                     │
                     ▼
            Data Store Public API
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
 Dataset Store  Metadata Store  Artifact Store
        │            │            │
        ├────────────┼────────────┤
                     ▼
              Version Manager
                     │
                     ▼
              Lineage Registry
                     │
                     ▼
         Transaction & Storage Layer
                     │
                     ▼
        Infraestrutura de Persistência
```

Cada camada possui responsabilidades específicas e comunica-se apenas por contratos institucionais.

---

# Componentes Institucionais

A arquitetura do Data Store é composta pelos seguintes componentes principais:

- Data Store Public API;
- Dataset Store;
- Metadata Store;
- Artifact Store;
- Configuration Store;
- Version Manager;
- Lineage Registry;
- Transaction Manager;
- Storage Provider;
- Observability Services;
- Governance Services.

Esses componentes representam a organização lógica da arquitetura e não necessariamente correspondem a módulos físicos.

---

# Data Store Public API

A Public API representa o único ponto oficial de acesso ao Data Store.

Suas responsabilidades incluem:

- receber solicitações de persistência;
- recuperar ativos;
- publicar versões;
- consultar metadados;
- expor contratos públicos;
- abstrair completamente a infraestrutura física.

Nenhum consumidor acessa diretamente a camada de armazenamento.

---

# Dataset Store

Responsável pelo armazenamento dos Datasets produzidos pela plataforma.

Entre suas atribuições:

- persistência dos estados oficiais dos Datasets;
- recuperação de versões;
- gerenciamento de identificadores;
- manutenção da integridade dos dados.

---

# Metadata Store

Responsável pelo armazenamento dos metadados institucionais.

Inclui informações como:

- identificação;
- classificação;
- origem;
- estrutura;
- esquema;
- datas;
- autorias;
- políticas;
- informações técnicas.

Os metadados permanecem independentes do conteúdo dos Datasets.

---

# Artifact Store

Armazena todos os artefatos produzidos pelo ecossistema.

Exemplos:

- relatórios;
- snapshots;
- arquivos exportados;
- resultados intermediários;
- objetos derivados;
- documentos produzidos pelos Engines.

---

# Configuration Store

Responsável pela persistência das configurações institucionais.

Inclui:

- parâmetros do Data Pipeline;
- configurações dos Engines;
- políticas de governança;
- configurações operacionais;
- parâmetros de execução.

---

# Version Manager

Gerencia o ciclo de vida das versões persistidas.

Suas responsabilidades incluem:

- criação de versões;
- identificação única;
- imutabilidade;
- publicação;
- recuperação;
- histórico completo.

Nenhum ativo institucional existe sem versionamento.

---

# Lineage Registry

Mantém o registro oficial das relações entre os ativos.

Controla:

- origem;
- dependências;
- transformações;
- publicações;
- consumidores;
- artefatos derivados.

O Lineage Registry fornece rastreabilidade completa do ecossistema.

---

# Transaction Manager

Coordena operações que exigem consistência transacional.

Entre suas responsabilidades:

- controle de transações;
- confirmação (commit);
- reversão (rollback);
- isolamento;
- recuperação em caso de falhas.

Sua implementação permanece independente da tecnologia utilizada.

---

# Storage Provider

Representa a abstração da infraestrutura física.

Pode utilizar diferentes mecanismos de armazenamento sem alterar os contratos públicos.

Exemplos de implementações possíveis incluem:

- bancos relacionais;
- bancos NoSQL;
- armazenamento orientado a objetos;
- Data Lakes;
- Data Warehouses;
- sistemas distribuídos.

A arquitetura não estabelece preferência por nenhuma tecnologia.

---

# Observabilidade

Todos os componentes devem produzir informações operacionais.

Entre elas:

- métricas;
- logs;
- eventos;
- tempos de resposta;
- utilização de recursos;
- falhas.

Essas informações são disponibilizadas aos serviços institucionais de observabilidade.

---

# Governança

A governança atua transversalmente sobre todos os componentes.

Suas responsabilidades incluem:

- auditoria;
- retenção;
- classificação;
- conformidade;
- controle de acesso;
- políticas institucionais.

Nenhum ativo é persistido fora das políticas definidas pela plataforma.

---

# Organização Modular

A arquitetura foi concebida para permitir evolução incremental.

Novos componentes poderão ser incorporados preservando:

- contratos públicos;
- compatibilidade;
- independência tecnológica;
- baixo acoplamento;
- alta coesão.

---

# Próxima Seção

A próxima seção apresenta o Modelo de Armazenamento institucional, definindo como os diferentes tipos de ativos são organizados e persistidos no Data Store.