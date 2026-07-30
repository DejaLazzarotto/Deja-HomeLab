# 10. Convenções

## Objetivo

Este documento estabelece as convenções oficiais de desenvolvimento da Deja Indicadores.

Seu objetivo é garantir uniformidade na implementação, facilitar a colaboração entre desenvolvedores, reduzir inconsistências e preservar a qualidade arquitetural do produto durante toda a sua evolução.

---

## Princípios

As convenções adotadas seguem os seguintes princípios:

- consistência;
- simplicidade;
- legibilidade;
- previsibilidade;
- reutilização;
- padronização institucional;
- rastreabilidade.

Toda implementação deverá observar estas convenções independentemente da tecnologia utilizada.

---

## Organização do Código

O código deverá ser organizado de forma clara e coerente com a Arquitetura de Implementação.

Entre as diretrizes gerais:

- responsabilidades bem definidas;
- módulos coesos;
- baixo acoplamento;
- nomenclatura consistente;
- separação entre domínio, aplicação e infraestrutura;
- eliminação de duplicações sempre que possível.

---

## Nomenclatura

Os nomes utilizados no código deverão ser claros, objetivos e representativos de sua responsabilidade.

Devem ser evitadas:

- abreviações desnecessárias;
- nomes genéricos;
- identificadores ambíguos;
- terminologia inconsistente.

A terminologia adotada deverá permanecer alinhada ao glossário institucional da Deja Platform e da Deja Indicadores.

---

## Documentação

Toda implementação relevante deverá possuir documentação correspondente.

Sempre que houver alterações estruturais ou arquiteturais, a documentação deverá ser atualizada antes ou em conjunto com a implementação.

A documentação constitui parte integrante do produto.

---

## Tratamento de Dependências

As dependências deverão ser reduzidas ao mínimo necessário.

Sempre que possível, a comunicação entre componentes deverá ocorrer por contratos públicos, preservando o encapsulamento das implementações.

Dependências circulares não são permitidas.

---

## Revisões

Toda alteração significativa deverá ser submetida ao processo institucional de revisão técnica.

As revisões deverão verificar:

- conformidade arquitetural;
- aderência às convenções;
- qualidade da implementação;
- reutilização de componentes;
- atualização da documentação;
- existência dos testes correspondentes.

---

## Evolução

As convenções poderão evoluir conforme o amadurecimento da plataforma e do produto.

Alterações deverão preservar compatibilidade com os princípios arquiteturais e ser formalmente documentadas.

---

## Governança

Estas convenções constituem referência obrigatória para toda a implementação da Deja Indicadores.

Exceções deverão ser justificadas, documentadas e aprovadas conforme o processo institucional de governança arquitetural.