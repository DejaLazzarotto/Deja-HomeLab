# Fontes de Dados

## Objetivo

Este documento estabelece as diretrizes institucionais para documentação das fontes de dados utilizadas pelos indicadores da Deja Indicadores.

Seu objetivo é garantir que toda informação utilizada nos cálculos seja identificável, rastreável, consistente e passível de validação ao longo de todo o ciclo de vida do produto.

---

# Princípios

Toda fonte de dados deverá:

- possuir origem claramente identificada;
- apresentar definição funcional;
- possuir rastreabilidade completa;
- permitir auditoria dos cálculos;
- permanecer independente da tecnologia utilizada para armazenamento;
- possuir documentação suficiente para sua implementação.

Nenhum indicador poderá depender de fontes de dados não documentadas.

---

# Conceito de Fonte de Dados

Uma fonte de dados representa qualquer conjunto estruturado de informações utilizado na composição de um indicador.

Uma fonte poderá corresponder, por exemplo, a:

- entidade de domínio;
- conjunto de registros;
- serviço interno;
- API externa;
- processo de integração;
- arquivo importado;
- sistema legado;
- serviço da Deja Platform.

O catálogo documenta a origem lógica das informações, independentemente da forma física de armazenamento.

---

# Identificação

Cada fonte deverá possuir, no mínimo:

- identificador;
- nome;
- descrição;
- domínio de negócio;
- responsável funcional;
- responsável técnico;
- status.

Essas informações facilitam a governança e a manutenção das dependências dos indicadores.

---

# Estrutura dos Dados

A documentação deverá informar:

- entidades envolvidas;
- atributos utilizados;
- chaves de relacionamento;
- cardinalidade;
- regras de integridade;
- restrições conhecidas.

Essas definições estabelecem a base para implementação dos cálculos.

---

# Origem das Informações

Cada indicador deverá indicar explicitamente a origem de seus dados.

As origens poderão incluir:

- cadastros internos;
- movimentações operacionais;
- documentos fiscais;
- registros financeiros;
- integrações com ERPs;
- integrações com CRMs;
- APIs de terceiros;
- planilhas importadas;
- arquivos de intercâmbio;
- serviços da Deja Platform.

Quando múltiplas fontes forem utilizadas, todas deverão ser documentadas.

---

# Atualização dos Dados

A documentação deverá especificar como os dados são atualizados.

Exemplos:

- tempo real;
- sob demanda;
- processamento em lote;
- atualização diária;
- atualização mensal;
- sincronização externa;
- importação manual.

Essa informação é essencial para interpretação dos resultados dos indicadores.

---

# Qualidade dos Dados

Os indicadores dependem diretamente da qualidade das informações utilizadas.

A documentação deverá registrar:

- requisitos mínimos de consistência;
- tratamento de registros inválidos;
- tratamento de duplicidades;
- tratamento de dados ausentes;
- regras de validação;
- critérios de aceitação.

Esses critérios deverão ser considerados durante a implementação e os testes.

---

# Dependências

Cada fonte poderá depender de outras informações previamente consolidadas.

Essas dependências deverão ser explicitadas para permitir:

- planejamento da implementação;
- rastreamento de impactos;
- identificação de riscos;
- validação dos cálculos.

---

# Segurança

Sempre que aplicável, a documentação deverá indicar requisitos relacionados à segurança das informações, incluindo:

- controle de acesso;
- confidencialidade;
- integridade;
- rastreabilidade de alterações;
- conformidade regulatória.

A documentação funcional não substitui os mecanismos técnicos de proteção dos dados, mas estabelece seus requisitos.

---

# Rastreabilidade

Toda fonte de dados deverá manter vínculo com:

- indicadores que a utilizam;
- módulos funcionais;
- funcionalidades relacionadas;
- especificações funcionais;
- componentes técnicos responsáveis pelo processamento.

Essa rastreabilidade facilita análises de impacto e evolução do produto.

---

# Evolução

Novas fontes de dados poderão ser incorporadas ao produto sem alterações na estrutura institucional definida neste documento.

Toda nova fonte deverá ser documentada antes de ser utilizada por qualquer indicador, preservando a consistência, a governança e a rastreabilidade do Catálogo Oficial de Indicadores.