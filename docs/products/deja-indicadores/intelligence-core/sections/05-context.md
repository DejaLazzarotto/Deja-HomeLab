# 05. Context

O Context representa o estado institucional compartilhado durante a execução do Intelligence Core.

Seu objetivo é disponibilizar um ambiente comum para circulação de informações entre os componentes da infraestrutura e os Engines especializados, eliminando dependências diretas entre eles.

O Context não contém regras de negócio. Sua responsabilidade limita-se ao armazenamento, disponibilização e gerenciamento das informações necessárias para a execução coordenada do ecossistema.

## Responsabilidades

Compete ao Context:

- manter o estado compartilhado da execução;
- disponibilizar informações institucionais aos componentes autorizados;
- fornecer dados necessários para os Pipelines;
- armazenar referências de execução;
- compartilhar metadados entre os Engines;
- disponibilizar configurações resolvidas durante a execução;
- suportar mecanismos de rastreabilidade;
- fornecer informações para observabilidade.

## Estrutura conceitual

O Context é composto por diferentes conjuntos de informações institucionais.

```text
                 Intelligence Context
                         │
     ┌───────────────────┼───────────────────┐
     │                   │                   │
 Execution Data     Shared Metadata     Configuration
     │                   │                   │
     ├──────────────┬────┴────┬──────────────┤
     │              │         │              │
 References     Runtime Info  Policies    Trace Data
```

Cada conjunto possui finalidade específica e pode ser consumido por diferentes componentes do Core, respeitando os contratos públicos estabelecidos.

## Compartilhamento entre Engines

Os Engines não compartilham informações diretamente entre si.

Toda informação institucional utilizada durante a execução é disponibilizada por intermédio do Context, que atua como mecanismo oficial de intercâmbio de estado.

Essa abordagem reduz o acoplamento arquitetural e permite que cada Engine permaneça independente da implementação dos demais.

## Escopo do Context

O Context existe apenas durante o ciclo de vida da execução coordenada pelo Runtime.

Sua utilização não substitui mecanismos permanentes de persistência, responsabilidade que permanece sob os componentes apropriados do ecossistema.

## Evolução

Novas categorias de informações poderão ser incorporadas ao Context desde que preservem os contratos institucionais existentes e não introduzam dependências diretas entre os Engines.

Dessa forma, o Context mantém-se como um mecanismo genérico, extensível e independente das regras de negócio da Deja Indicadores.