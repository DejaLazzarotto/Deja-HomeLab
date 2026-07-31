# 4. Modelo de Log

## Objetivo

Esta seção define o modelo institucional utilizado pelo Execution Log para representar os registros técnicos produzidos durante a execução da Deja Platform.

O modelo estabelece uma estrutura padronizada para todos os componentes da plataforma, permitindo armazenamento consistente, consultas eficientes, rastreabilidade completa e evolução controlada.

---

## Registro de Log

A menor unidade de informação do Execution Log é o **Log Record**.

Cada Log Record representa um único evento técnico produzido por um componente autorizado da plataforma.

Após sua persistência, o registro passa a representar um fato técnico ocorrido durante a operação da plataforma.

---

## Características

Todo Log Record deve possuir as seguintes características:

- identificador único;
- origem conhecida;
- instante de ocorrência;
- nível de severidade;
- contexto operacional;
- mensagem técnica;
- metadados associados;
- rastreabilidade completa.

Essas características garantem uniformidade entre todos os registros produzidos.

---

## Estrutura conceitual

Conceitualmente, um Log Record é composto por:

- identificação;
- informações temporais;
- origem;
- categoria;
- severidade;
- mensagem;
- contexto;
- detalhes técnicos;
- metadados.

A estrutura física poderá variar conforme a tecnologia utilizada, preservando sempre o modelo institucional.

---

## Classificação

Os registros podem ser classificados segundo diferentes dimensões.

Entre elas:

- componente de origem;
- serviço responsável;
- módulo;
- categoria funcional;
- ambiente;
- tipo de evento;
- criticidade;
- severidade.

Essa classificação facilita consultas e análises operacionais.

---

## Contexto operacional

Sempre que disponível, o registro deve manter vínculo com o contexto em que foi produzido.

Esse contexto pode incluir:

- Execution Request;
- execução;
- workflow;
- operação;
- usuário;
- sessão;
- tenant;
- ambiente;
- correlação distribuída.

O objetivo é permitir reconstrução técnica das operações realizadas.

---

## Metadados

Além da mensagem principal, o Log Record pode conter metadados adicionais.

Exemplos:

- duração da operação;
- identificadores institucionais;
- versões;
- endereço do serviço;
- informações de infraestrutura;
- parâmetros técnicos;
- códigos internos.

Esses metadados ampliam a capacidade de diagnóstico e observabilidade.

---

## Imutabilidade lógica

Após sua persistência, o conteúdo do Log Record não deve ser alterado.

Caso seja necessário complementar informações, novos registros devem ser produzidos, preservando a sequência cronológica e a integridade histórica dos eventos.

---

## Compatibilidade

O modelo institucional foi concebido para evoluir de forma incremental.

Novos campos poderão ser adicionados futuramente sem comprometer a interpretação dos registros existentes, preservando compatibilidade entre versões da arquitetura.