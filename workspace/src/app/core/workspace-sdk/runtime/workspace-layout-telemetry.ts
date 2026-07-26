/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Telemetry
 *
 * Infraestrutura institucional responsável pela coleta
 * e agregação das métricas operacionais do Workspace Layout.
 */

import {
  WorkspaceLayoutMetricOperation,
  WorkspaceLayoutMetricRecord,
  WorkspaceLayoutMetrics,
  WorkspaceLayoutMetricSummary,
} from './workspace-layout-metrics';

/**
 * Implementação institucional padrão das métricas do
 * Workspace Layout.
 *
 * As métricas permanecem integralmente em memória,
 * permitindo futura integração com mecanismos externos
 * de telemetria, monitoramento e observabilidade.
 */
export class WorkspaceLayoutTelemetry
  implements WorkspaceLayoutMetrics {

  private readonly summaries =
    new Map<
      WorkspaceLayoutMetricOperation,
      WorkspaceLayoutMetricSummary
    >();

  /**
   * Registra uma operação concluída.
   */
  record(
    record: WorkspaceLayoutMetricRecord,
  ): void {

    const current =
      this.summaries.get(record.operation);

    const executions =
      (current?.executions ?? 0) + 1;

    const succeeded =
      (current?.succeeded ?? 0)
      + (record.outcome === 'succeeded' ? 1 : 0);

    const rejected =
      (current?.rejected ?? 0)
      + (record.outcome === 'rejected' ? 1 : 0);

    const failed =
      (current?.failed ?? 0)
      + (record.outcome === 'failed' ? 1 : 0);

    const totalDuration =
      (current?.totalDuration ?? 0)
      + record.duration;

    this.summaries.set(
      record.operation,
      {
        operation: record.operation,
        executions,
        succeeded,
        rejected,
        failed,
        totalDuration,
        averageDuration:
          executions === 0
            ? 0
            : totalDuration / executions,
      },
    );

  }

  /**
   * Retorna o resumo agregado de uma operação.
   */
  getSummary(
    operation: WorkspaceLayoutMetricOperation,
  ): WorkspaceLayoutMetricSummary {

    return (
      this.summaries.get(operation)
      ?? {
        operation,
        executions: 0,
        succeeded: 0,
        rejected: 0,
        failed: 0,
        totalDuration: 0,
        averageDuration: 0,
      }
    );

  }

  /**
   * Retorna todas as métricas agregadas.
   */
  getSummaries():
    readonly WorkspaceLayoutMetricSummary[] {

    return [
      ...this.summaries.values(),
    ];

  }

  /**
   * Remove todas as métricas coletadas.
   */
  clear(): void {

    this.summaries.clear();

  }

}