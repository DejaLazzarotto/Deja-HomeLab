# 08. Services

Os Services representam o conjunto institucional de serviços compartilhados disponibilizados pelo Intelligence Core.

Sua finalidade é concentrar funcionalidades reutilizáveis da infraestrutura, permitindo que os Engines consumam capacidades comuns sem necessidade de implementar soluções próprias.

Os Services não implementam regras de negócio. Sua responsabilidade limita-se ao fornecimento de capacidades técnicas reutilizáveis e independentes do domínio funcional da Deja Indicadores.

## Responsabilidades

Compete aos Services:

- disponibilizar funcionalidades reutilizáveis;
- encapsular capacidades comuns da infraestrutura;
- reduzir duplicação de implementação entre os Engines;
- padronizar o acesso aos recursos institucionais;
- apoiar o Runtime durante a execução;
- integrar-se ao Event Bus, Registry e Configuration;
- fornecer informações para Observability e Traceability.

## Organização dos Services

Os Services são organizados por responsabilidade arquitetural.

```text
               Intelligence Services
                        │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
 Runtime Services   Context Services   Pipeline Services
    │                   │                   │
    ├──────────────┬────┴────┬──────────────┤
    │              │         │              │
 Event Services Registry Services Config Services
    │              │         │              │
    └──────────────┴─────────┴──────────────┘
                        │
         Observability / Traceability
```

Cada grupo de serviços atende a uma responsabilidade específica da infraestrutura, preservando alta coesão e baixo acoplamento.

## Consumo pelos Engines

Os Engines acessam funcionalidades compartilhadas exclusivamente por meio dos contratos públicos disponibilizados pelos Services.

Não é permitido o consumo direto de implementações internas de outros Engines ou componentes da infraestrutura.

Essa abordagem garante isolamento arquitetural e facilita a evolução independente das implementações.

## Ciclo de vida

Os Services são gerenciados pelo Runtime do Intelligence Core.

Durante a inicialização, os serviços necessários são registrados e disponibilizados para consumo pelos componentes autorizados.

Ao término da execução, seus recursos são liberados conforme as políticas definidas pelo Lifecycle.

## Extensibilidade

Novos Services poderão ser adicionados ao Intelligence Core sempre que representarem capacidades reutilizáveis da infraestrutura.

A introdução de novos serviços não deverá exigir alterações nos consumidores existentes, desde que os contratos públicos permaneçam compatíveis.

## Evolução

O catálogo institucional de Services deverá evoluir continuamente para atender às novas necessidades da plataforma, preservando compatibilidade arquitetural, estabilidade operacional e independência entre infraestrutura e regras de negócio.