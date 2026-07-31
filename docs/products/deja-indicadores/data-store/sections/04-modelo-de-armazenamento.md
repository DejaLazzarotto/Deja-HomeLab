# 04. Modelo de Armazenamento

## Objetivo

Esta seção define o modelo institucional de armazenamento do Data Store.

O modelo estabelece como os diferentes ativos persistentes da Deja Indicadores são organizados, identificados, versionados e disponibilizados aos componentes consumidores, mantendo independência das tecnologias físicas de armazenamento.

---

# Modelo Lógico

O Data Store organiza seus ativos em um modelo lógico composto por repositórios especializados.

Cada repositório é responsável por um tipo específico de ativo institucional.

A organização lógica pode ser representada da seguinte forma:

```
                 Data Store
                      │
      ┌───────────────┼────────────────┐
      ▼               ▼                ▼
 Dataset Store   Metadata Store   Artifact Store
      │               │                │
      ├───────────────┼────────────────┤
                      ▼
             Configuration Store
                      │
                      ▼
              Version Manager
                      │
                      ▼
               Lineage Registry
```

Essa estrutura é independente da forma como os dados serão armazenados fisicamente.

---

# Unidades de Armazenamento

Os principais ativos persistidos pelo Data Store são:

- Dataset;
- Metadata;
- Artifact;
- Configuration;
- Version;
- Lineage Record;
- Audit Record.

Cada unidade possui identidade própria, ciclo de vida independente e políticas específicas de governança.

---

# Identificação dos Ativos

Todo ativo armazenado deve possuir um identificador institucional único.

Esse identificador deve ser:

- permanente;
- imutável;
- independente da tecnologia;
- reutilizável em todo o ecossistema.

A identidade de um ativo nunca depende de sua localização física.

---

# Separação entre Conteúdo e Metadados

O conteúdo de um ativo e seus metadados são tratados como entidades distintas.

Essa separação permite:

- evolução independente;
- consultas otimizadas;
- indexação eficiente;
- governança específica;
- redução de acoplamento.

Os metadados descrevem o ativo, mas não fazem parte de seu conteúdo.

---

# Organização por Domínio

Os ativos podem ser organizados logicamente por domínio funcional.

Exemplos:

- Financeiro;
- Comercial;
- Produção;
- Logística;
- Recursos Humanos;
- Qualidade.

Essa organização facilita navegação, governança e administração.

---

# Organização por Categoria

Além do domínio, os ativos podem ser classificados por categoria.

Exemplos:

- Dataset;
- Indicador;
- Configuração;
- Relatório;
- Snapshot;
- Artefato;
- Documento Técnico.

Essa classificação não altera a identidade do ativo.

---

# Organização por Versão

Cada ativo pode possuir múltiplas versões.

O modelo institucional estabelece que:

- versões são independentes;
- versões publicadas são imutáveis;
- versões preservam histórico completo;
- consumidores podem acessar versões específicas.

Não existe substituição física de versões anteriores.

---

# Armazenamento de Lineage

As relações entre ativos são armazenadas separadamente.

Cada registro de lineage descreve, por exemplo:

- origem do ativo;
- ativos de entrada;
- ativos derivados;
- transformações realizadas;
- publicações;
- dependências.

O lineage forma um grafo institucional de rastreabilidade.

---

# Armazenamento de Configurações

As configurações da plataforma são persistidas como ativos próprios.

Isso permite:

- versionamento;
- auditoria;
- restauração;
- rastreabilidade;
- evolução controlada.

Configurações nunca permanecem apenas em memória durante seu ciclo de vida institucional.

---

# Armazenamento de Artefatos

Artefatos representam objetos produzidos durante a execução da plataforma.

Exemplos:

- relatórios;
- exportações;
- arquivos temporários promovidos;
- snapshots;
- resultados intermediários;
- documentos gerados.

Cada artefato pode possuir metadados, versionamento e lineage próprios.

---

# Abstração da Persistência Física

O modelo lógico não estabelece como os ativos serão armazenados fisicamente.

A implementação poderá utilizar diferentes tecnologias, incluindo:

- bancos relacionais;
- bancos NoSQL;
- armazenamento em objetos;
- sistemas de arquivos distribuídos;
- Data Lakes;
- Data Warehouses;
- soluções híbridas.

Os contratos públicos permanecem inalterados independentemente da infraestrutura escolhida.

---

# Benefícios do Modelo

O modelo de armazenamento proporciona:

- desacoplamento entre domínio e infraestrutura;
- alta flexibilidade tecnológica;
- organização consistente dos ativos;
- facilidade de evolução;
- rastreabilidade completa;
- governança centralizada;
- reutilização dos dados persistidos;
- suporte a múltiplas estratégias de armazenamento.

---

# Próxima Seção

A próxima seção detalha o modelo institucional de armazenamento dos Datasets, principal ativo persistido pela plataforma.