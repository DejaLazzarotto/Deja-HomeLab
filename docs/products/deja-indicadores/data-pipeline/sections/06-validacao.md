# 06. Validação

## Objetivo

A Validação é responsável por verificar a integridade, consistência e qualidade dos dados produzidos pela etapa de Aquisição.

Seu objetivo é impedir que dados inválidos, incompletos ou inconsistentes avancem para as etapas seguintes do Data Pipeline.

Todo conjunto de dados deverá ser validado antes de qualquer transformação, normalização ou enriquecimento.

---

## Papel na Arquitetura

A Validação representa a primeira barreira de qualidade do Data Pipeline.

```text
Raw Dataset
      │
      ▼
 Validation
      │
      ├────────► Rejeição
      │
      ▼
Validated Dataset
```

Somente conjuntos aprovados poderão seguir para processamento.

---

## Responsabilidades

A etapa de Validação possui as seguintes responsabilidades:

- verificar estrutura;
- validar tipos de dados;
- validar obrigatoriedade de campos;
- verificar integridade;
- identificar inconsistências;
- identificar duplicidades;
- calcular métricas de qualidade;
- registrar evidências da validação;
- classificar erros encontrados.

---

## Níveis de Validação

A arquitetura institucional define diferentes níveis de validação.

### Validação Estrutural

Verifica se a estrutura recebida corresponde ao contrato esperado.

Exemplos:

- campos existentes;
- ordem esperada;
- formatos;
- tipos básicos.

---

### Validação Sintática

Verifica se os valores respeitam o formato esperado.

Exemplos:

- datas;
- CPF/CNPJ;
- e-mail;
- números;
- códigos.

---

### Validação Semântica

Verifica o significado dos dados.

Exemplos:

- datas futuras proibidas;
- valores negativos inválidos;
- códigos inexistentes;
- domínio permitido.

---

### Validação de Integridade

Confirma relações entre registros.

Exemplos:

- chaves;
- referências;
- unicidade;
- consistência entre entidades.

---

### Validação de Completude

Avalia a presença das informações obrigatórias.

São analisados:

- campos obrigatórios;
- percentual de preenchimento;
- registros incompletos;
- ausência de informações críticas.

---

## Regras de Validação

Cada fonte poderá possuir regras específicas.

As regras deverão ser declarativas e versionadas.

Exemplos:

```text
Campo obrigatório
Valor mínimo
Valor máximo
Lista permitida
Expressão regular
Relacionamento obrigatório
```

As regras não deverão ser codificadas diretamente nos conectores.

---

## Resultado da Validação

Ao término da execução, o conjunto de dados receberá um dos seguintes estados:

- Aprovado;
- Aprovado com Avisos;
- Rejeitado.

Dados rejeitados não poderão prosseguir no pipeline.

---

## Qualidade dos Dados

A Validação deverá produzir indicadores institucionais de qualidade.

Exemplos:

- percentual de registros válidos;
- percentual de registros rejeitados;
- campos incompletos;
- duplicidades;
- inconsistências encontradas;
- taxa de conformidade.

Essas métricas poderão ser utilizadas pelo Intelligence Core e pelos mecanismos de observabilidade.

---

## Tratamento de Erros

Os erros identificados deverão ser classificados.

Categorias sugeridas:

- erro estrutural;
- erro sintático;
- erro semântico;
- erro de integridade;
- erro de configuração;
- erro de origem.

Cada ocorrência deverá registrar evidências suficientes para auditoria.

---

## Metadados Produzidos

A Validação deverá registrar, no mínimo:

- Pipeline Execution ID;
- versão das regras;
- quantidade de registros analisados;
- quantidade aprovada;
- quantidade rejeitada;
- métricas de qualidade;
- duração;
- evidências da validação.

---

## Eventos

Durante a Validação poderão ser publicados:

- ValidationStarted;
- ValidationCompleted;
- ValidationFailed;
- DatasetApproved;
- DatasetRejected;
- QualityMetricsGenerated.

Todos os eventos são distribuídos pelo Event Bus institucional.

---

## Integração

A etapa de Validação comunica-se com:

- Pipeline Runtime;
- Pipeline Context;
- Registry;
- Event Bus;
- Observability;
- Metadata Registry.

Após aprovação, produz o **Validated Dataset**, que será consumido pelas etapas seguintes.

---

## Princípio Institucional

Nenhum conjunto de dados poderá ser disponibilizado às etapas posteriores do Data Pipeline sem ter sido validado segundo as regras institucionais vigentes.

A qualidade dos dados constitui um requisito arquitetural obrigatório da Deja Indicadores e prevalece sobre desempenho ou conveniência operacional.