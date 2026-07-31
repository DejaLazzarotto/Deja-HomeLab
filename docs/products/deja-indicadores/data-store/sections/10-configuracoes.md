# 10. Configurações

## Objetivo

Esta seção define a arquitetura institucional de persistência das Configurações no Data Store.

As configurações representam os parâmetros utilizados para controlar o comportamento dos componentes da Deja Indicadores, permitindo padronização operacional, rastreabilidade das alterações e evolução controlada da plataforma.

---

# Conceito

Uma configuração é um ativo institucional que define parâmetros de funcionamento de um ou mais componentes do ecossistema.

As configurações não representam lógica de negócio, mas sim informações utilizadas para parametrizar a execução da plataforma.

Toda configuração relevante deve ser persistida pelo Data Store.

---

# Escopo

O modelo contempla configurações relacionadas a:

- Data Pipeline;
- Intelligence Core;
- Indicator Catalog;
- Knowledge Base;
- Diagnostic Engine;
- Decision Engine;
- Recommendation Engine;
- Observabilidade;
- Governança;
- Runtime Institucional.

Cada componente permanece responsável pela interpretação de suas próprias configurações.

---

# Estrutura Lógica

Cada configuração é composta, logicamente, pelos seguintes elementos:

- identificador;
- nome;
- descrição;
- componente proprietário;
- categoria;
- conjunto de parâmetros;
- versão;
- estado;
- metadados;
- informações de auditoria.

A organização física desses elementos é independente da arquitetura.

---

# Classificação

As configurações podem ser classificadas conforme sua finalidade.

Exemplos:

- operacionais;
- funcionais;
- técnicas;
- segurança;
- integração;
- observabilidade;
- governança;
- desempenho.

Uma configuração pode pertencer a mais de uma classificação.

---

# Versionamento

Toda configuração é obrigatoriamente versionada.

Uma alteração em qualquer parâmetro resulta na criação de uma nova versão.

Versões publicadas permanecem imutáveis, garantindo previsibilidade e reprodutibilidade do comportamento da plataforma.

---

# Publicação

Uma configuração somente poderá ser utilizada pelos componentes após sua publicação.

Durante esse processo devem ser registrados:

- versão publicada;
- momento da publicação;
- responsável;
- registros de auditoria;
- relações de lineage, quando aplicáveis.

---

# Relação com o Lineage

As configurações também participam do modelo institucional de Lineage.

É possível registrar relações como:

- configuração utilizada por uma execução;
- configuração responsável por uma versão publicada;
- configurações derivadas;
- dependências entre configurações.

Essas informações ampliam a capacidade de auditoria da plataforma.

---

# Recuperação

Os consumidores podem recuperar configurações utilizando critérios como:

- identificador;
- componente;
- categoria;
- versão;
- estado;
- domínio;
- etiquetas.

Os mecanismos específicos são definidos pelos contratos públicos do Data Store.

---

# Governança

As configurações devem obedecer às políticas institucionais de:

- controle de acesso;
- versionamento;
- retenção;
- auditoria;
- conformidade;
- rastreabilidade.

Alterações não registradas são incompatíveis com a arquitetura da plataforma.

---

# Benefícios

O modelo institucional de persistência das configurações proporciona:

- centralização da parametrização;
- controle histórico completo;
- reprodutibilidade das execuções;
- redução de inconsistências;
- auditoria permanente;
- integração com o Lineage;
- governança consistente;
- independência tecnológica.

---

# Próxima Seção

A próxima seção apresenta a arquitetura de Transações do Data Store, responsável por garantir a consistência das operações de persistência realizadas pela plataforma.