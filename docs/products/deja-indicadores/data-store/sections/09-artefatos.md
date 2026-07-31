# 09. Artefatos

## Objetivo

Esta seção define a arquitetura institucional de persistência dos Artefatos no Data Store.

Artefatos representam todos os objetos produzidos durante a execução da plataforma que necessitam ser preservados, reutilizados ou auditados posteriormente.

Embora nem todo artefato represente um Dataset, todos constituem ativos institucionais sujeitos às políticas de persistência, versionamento, rastreabilidade e governança da Deja Indicadores.

---

# Conceito

Um artefato é qualquer objeto gerado por um processo da plataforma cuja persistência agregue valor operacional, técnico ou de negócio.

Os artefatos podem ser produzidos por diferentes componentes do ecossistema e possuir natureza estruturada ou não estruturada.

---

# Tipos de Artefatos

Exemplos de artefatos persistidos incluem:

- relatórios;
- dashboards exportados;
- snapshots;
- arquivos de importação;
- arquivos de exportação;
- documentos técnicos;
- resultados intermediários;
- modelos derivados;
- logs persistidos;
- evidências de execução;
- arquivos auxiliares.

A arquitetura permite a incorporação de novos tipos de artefatos sem necessidade de alterações estruturais.

---

# Responsabilidade do Data Store

O Data Store é responsável por:

- persistir artefatos;
- recuperar artefatos;
- versionar artefatos;
- registrar metadados;
- manter lineage;
- aplicar políticas de retenção;
- garantir rastreabilidade;
- disponibilizar consultas.

A geração do artefato permanece sob responsabilidade do componente produtor.

---

# Identificação

Todo artefato deve possuir um identificador institucional único.

Esse identificador permanece constante durante todo o ciclo de vida do artefato, independentemente da tecnologia de armazenamento utilizada.

Versões distintas compartilham a mesma identidade institucional, diferenciando-se apenas pelo identificador de versão.

---

# Metadados

Cada artefato deve possuir metadados próprios, incluindo, quando aplicável:

- nome;
- descrição;
- categoria;
- produtor;
- componente de origem;
- data de criação;
- versão;
- formato;
- tamanho;
- classificação;
- políticas aplicáveis.

Os metadados são armazenados separadamente do conteúdo do artefato.

---

# Versionamento

Artefatos seguem o mesmo modelo institucional de versionamento adotado pelos demais ativos.

Isso significa que:

- toda versão possui identidade própria;
- versões publicadas são imutáveis;
- novas alterações geram novas versões;
- o histórico permanece preservado.

---

# Relação com o Lineage

Todo artefato pode participar do grafo institucional de Lineage.

As relações podem registrar, por exemplo:

- Dataset que originou o artefato;
- execução responsável pela geração;
- indicador relacionado;
- diagnóstico associado;
- recomendação produzida;
- consumidores do artefato.

Essas informações permitem reconstruir completamente sua origem e utilização.

---

# Recuperação

Os consumidores poderão localizar artefatos utilizando critérios como:

- identificador;
- categoria;
- produtor;
- componente;
- período;
- versão;
- etiquetas;
- domínio funcional.

Os contratos públicos do Data Store definem os mecanismos de consulta.

---

# Governança

Todos os artefatos estão sujeitos às políticas institucionais de:

- retenção;
- auditoria;
- classificação;
- conformidade;
- controle de acesso;
- preservação histórica.

A eliminação física de artefatos deve respeitar as políticas de governança definidas pela plataforma.

---

# Benefícios

O modelo institucional de persistência de artefatos proporciona:

- preservação dos resultados produzidos;
- reutilização de ativos;
- auditoria completa;
- rastreabilidade ponta a ponta;
- integração com o Lineage;
- versionamento consistente;
- governança centralizada;
- independência tecnológica.

---

# Próxima Seção

A próxima seção apresenta a arquitetura de persistência das Configurações, responsáveis por armazenar os parâmetros institucionais e operacionais utilizados pelos componentes da Deja Indicadores.