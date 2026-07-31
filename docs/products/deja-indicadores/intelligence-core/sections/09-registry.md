# 09. Registry

O Registry constitui o mecanismo institucional de registro, descoberta e resolução de componentes do Intelligence Core.

Sua responsabilidade é manter o catálogo dos elementos disponíveis durante a execução, permitindo que a infraestrutura e os Engines localizem capacidades institucionais de forma padronizada, desacoplada e independente de implementações concretas.

O Registry não executa lógica de negócio nem coordena o fluxo operacional do sistema. Sua função restringe-se ao gerenciamento das referências institucionais utilizadas pelo ecossistema.

## Responsabilidades

Compete ao Registry:

- registrar componentes institucionais;
- resolver componentes registrados;
- disponibilizar mecanismos de descoberta;
- manter identificadores institucionais;
- controlar versões de contratos quando aplicável;
- oferecer suporte ao Runtime durante a inicialização;
- fornecer informações para Observability;
- disponibilizar dados para Traceability.

## Componentes registrados

O Registry pode manter referências para diferentes categorias de componentes da infraestrutura.

```text
                 Intelligence Registry
                         │
     ┌───────────────────┼───────────────────┐
     │                   │                   │
   Engines           Services          Pipelines
     │                   │                   │
     ├──────────────┬────┴────┬──────────────┤
     │              │         │              │
 Event Types   Extension Points   Configurations
     │              │         │              │
     └──────────────┴─────────┴──────────────┘
                         │
                    Public APIs
```

Cada categoria é registrada de forma independente, preservando organização, isolamento e facilidade de evolução.

## Descoberta de componentes

A resolução de componentes ocorre exclusivamente por intermédio do Registry.

Os consumidores não dependem de implementações concretas nem de referências diretas entre si.

Essa abordagem reduz o acoplamento arquitetural e favorece a substituição ou evolução de implementações sem impacto sobre os demais componentes do ecossistema.

## Integração com o Runtime

Durante a inicialização do Intelligence Core, o Runtime registra os componentes institucionais necessários para a execução.

Ao longo do ciclo de vida da aplicação, o Registry permanece disponível como mecanismo oficial de descoberta e resolução, atendendo tanto à infraestrutura quanto aos Engines especializados.

## Extensibilidade

Novas categorias de componentes poderão ser registradas sem necessidade de alterações estruturais na arquitetura do Registry.

A expansão do catálogo institucional deve ocorrer por meio dos contratos públicos definidos pelo Intelligence Core.

## Evolução

O Registry deverá preservar estabilidade, compatibilidade e independência entre versões.

Sua evolução deverá ampliar a capacidade de descoberta e resolução de componentes sem comprometer os contratos existentes nem introduzir dependências diretas entre os participantes do ecossistema.