/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Tracing
 *
 * Infraestrutura institucional responsável pela instrumentação
 * das operações do Workspace Layout.
 */

import {
  WorkspaceLayoutMetricOperation,
  WorkspaceLayoutMetricOutcome,
  WorkspaceLayoutMetrics,
} from './workspace-layout-metrics';

/**
 * Instrumenta institucionalmente operações do
 * Workspace Layout Controller.
 *
 * A infraestrutura permanece completamente independente
 * do Workspace Runtime, Angular e mecanismos externos
 * de observabilidade.
 */
export class WorkspaceLayoutTracing {

  constructor(
    private readonly metrics: WorkspaceLayoutMetrics,
  ) {}

  /**
   * Executa uma operação instrumentada.
   */
  async trace<T>(
    operation: WorkspaceLayoutMetricOperation,
    action: () => Promise<T>,
  ): Promise<T> {

    const startedAt = Date.now();

    try {

      const result = await action();

      this.record(
        operation,
        'succeeded',
        startedAt,
      );

      return result;

    } catch (error) {

      this.record(
        operation,
        'failed',
        startedAt,
      );

      throw error;

    }

  }

  /**
   * Registra explicitamente uma operação rejeitada.
   */
  rejected(
    operation: WorkspaceLayoutMetricOperation,
    startedAt: number,
  ): void {

    this.record(
      operation,
      'rejected',
      startedAt,
    );

  }

  /**
   * Registra uma operação observada.
   */
  private record(
    operation: WorkspaceLayoutMetricOperation,
    outcome: WorkspaceLayoutMetricOutcome,
    startedAt: number,
  ): void {

    this.metrics.record({

      operation,

      outcome,

      duration: Date.now() - startedAt,

      timestamp: Date.now(),

    });

  }

}