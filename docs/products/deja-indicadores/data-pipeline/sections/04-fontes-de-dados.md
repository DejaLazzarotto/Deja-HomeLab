# 04. Fontes de Dados

## Objetivo

As Fontes de Dados representam todos os sistemas, serviços e repositórios capazes de fornecer informações para processamento pelo Data Pipeline.

A arquitetura institucional estabelece um modelo único para integração com diferentes origens de dados, preservando desacoplamento, extensibilidade e rastreabilidade.

Nenhuma fonte comunica-se diretamente com o Intelligence Core ou com os Engines especializados.

Toda aquisição ocorre exclusivamente por meio do Data Pipeline.

---

## Modelo Arquitetural

```text
                External Sources
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   Databases        APIs         File Systems
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
              Source Connectors
                       │
                       ▼
                Acquisition Layer
```

Os conectores abstraem completamente as características específicas de cada origem.

---

## Categorias de Fontes

O Data Pipeline suporta diferentes categorias de fontes de dados.

### Bancos de Dados

Incluem sistemas relacionais e analíticos.

Exemplos:

- PostgreSQL
- MySQL
- SQL Server
- Oracle
- SQLite
- MariaDB

Novos bancos poderão ser incorporados por meio de conectores especializados.

---

### APIs

Serviços externos disponibilizados por interfaces HTTP.

Podem utilizar:

- REST
- GraphQL
- Web Services
- APIs proprietárias

O protocolo utilizado não altera o funcionamento do pipeline.

---

### Arquivos

Dados provenientes de arquivos estruturados.

Exemplos:

- CSV
- Excel
- JSON
- XML
- Parquet
- Avro

Cada formato é interpretado pelo conector correspondente.

---

### Serviços Corporativos

Integrações com sistemas internos das organizações.

Exemplos:

- ERP
- CRM
- RH
- Financeiro
- Produção
- Estoque
- BI

Essas integrações seguem os mesmos contratos institucionais.

---

### Fontes em Tempo Real

O pipeline poderá consumir fluxos contínuos de dados.

Exemplos:

- filas de mensagens;
- eventos;
- streams;
- IoT;
- telemetria.

O processamento contínuo permanece compatível com a arquitetura geral.

---

## Source Connector

Cada fonte é representada por um Source Connector.

Responsabilidades:

- autenticação;
- conexão;
- leitura;
- paginação;
- tratamento de falhas;
- controle de timeout;
- reconexão;
- geração de metadados da origem.

O conector não executa transformações nem validações de negócio.

---

## Contrato Institucional

Todo Source Connector deverá implementar um contrato comum contendo, no mínimo:

- identificação da fonte;
- tipo da origem;
- versão;
- capacidades suportadas;
- configuração;
- estratégia de autenticação;
- estratégia de leitura;
- geração de metadados.

Esse contrato garante interoperabilidade entre todos os conectores.

---

## Configuração

Toda configuração de acesso deverá ser externa ao código.

Exemplos:

- credenciais;
- endpoints;
- portas;
- certificados;
- parâmetros de consulta;
- limites de leitura.

Nenhum valor sensível poderá ser incorporado à implementação.

---

## Identificação das Fontes

Cada fonte deverá possuir identificador institucional único.

Exemplo:

```text
SOURCE-ERP
SOURCE-CRM
SOURCE-INSS
SOURCE-CSV
SOURCE-API-IBGE
```

Esse identificador acompanha todo o ciclo de vida do processamento.

---

## Metadados

Durante a aquisição deverão ser registrados, no mínimo:

- identificador da fonte;
- data e hora da leitura;
- versão da origem;
- quantidade de registros;
- duração da aquisição;
- configuração utilizada;
- status da operação.

Esses metadados integram a rastreabilidade institucional.

---

## Tratamento de Falhas

O Data Pipeline deverá tratar falhas de comunicação sem comprometer os demais componentes.

Situações previstas incluem:

- indisponibilidade;
- autenticação inválida;
- timeout;
- dados incompletos;
- interrupção de conexão;
- inconsistência estrutural.

As falhas deverão ser registradas pelo sistema de observabilidade.

---

## Extensibilidade

Novas fontes poderão ser adicionadas sem alterações na arquitetura principal.

Basta implementar um novo Source Connector compatível com o contrato institucional.

Essa estratégia garante evolução incremental da plataforma.

---

## Princípio Institucional

Toda aquisição de dados da Deja Indicadores deverá ocorrer exclusivamente por meio de Source Connectors homologados pelo Data Pipeline, preservando padronização, segurança, rastreabilidade e independência entre as fontes de dados e o restante do ecossistema de inteligência.