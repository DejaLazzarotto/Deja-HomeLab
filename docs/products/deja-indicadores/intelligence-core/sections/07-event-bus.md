# 07. Event Bus

O Event Bus constitui o mecanismo institucional de comunicação orientada a eventos do Intelligence Core.

Sua responsabilidade é permitir que componentes da infraestrutura e Engines especializados publiquem e consumam eventos de forma desacoplada, preservando a independência arquitetural do ecossistema.

O Event Bus não implementa regras de negócio nem coordena fluxos de execução. Sua função é exclusivamente transportar eventos institucionais entre produtores e consumidores autorizados.

## Responsabilidades

Compete ao Event Bus:

- publicar eventos institucionais;
- distribuir eventos aos assinantes;
- desacoplar produtores e consumidores;
- permitir múltiplos assinantes para um mesmo evento;
- preservar a ordem lógica de publicação quando aplicável;
- registrar informações para observabilidade;
- fornecer dados para rastreabilidade;
- suportar evolução incremental do ecossistema.

## Modelo de comunicação

O Event Bus adota um modelo Publish/Subscribe.

```text
                 Event Bus
                     │
      ┌──────────────┼──────────────┐
      │              │              │
 Publish         Subscribe      Dispatch
      │              │              │
      └──────────────┼──────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   Runtime      Infrastructure   Engines
```

Os componentes publicam eventos sem conhecer seus consumidores, enquanto os consumidores registram interesse em tipos específicos de eventos sem depender da origem de sua publicação.

## Eventos institucionais

Os eventos transportados pelo Event Bus representam fatos relevantes ocorridos durante o funcionamento do ecossistema.

Exemplos incluem:

- inicialização do Runtime;
- início e término de Pipelines;
- mudanças de estado do Lifecycle;
- registro de componentes;
- resolução de configurações;
- execução de Engines;
- ocorrência de falhas institucionais;
- emissão de métricas operacionais.

O conteúdo específico de cada evento é definido pelos contratos públicos do Intelligence Core.

## Integração com o Core

O Event Bus integra-se aos demais componentes da infraestrutura institucional.

Durante a execução, eventos podem ser publicados pelo Runtime, Pipeline, Lifecycle, Services, Registry, Configuration, Observability e pelos próprios Engines.

Essa integração fornece uma visão consistente dos acontecimentos do ecossistema sem criar dependências diretas entre seus participantes.

## Escalabilidade

A arquitetura do Event Bus permite que novos tipos de eventos e novos consumidores sejam incorporados sem necessidade de alterações nos produtores existentes.

Essa característica favorece a expansão incremental do ecossistema e reduz o impacto arquitetural da introdução de novos componentes.

## Evolução

O Event Bus deverá evoluir preservando compatibilidade entre versões dos contratos de eventos.

Novas categorias de eventos poderão ser adicionadas sem comprometer consumidores existentes, garantindo estabilidade e evolução contínua da arquitetura do Intelligence Core.