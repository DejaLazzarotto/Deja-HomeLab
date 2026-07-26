/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Observability
 *
 * Infraestrutura institucional responsável pela coordenação
 * da observabilidade do Workspace Layout.
 */

import {
  WorkspaceLayoutDiagnosticSnapshot,
  WorkspaceLayoutDiagnostics,
} from './workspace-layout-diagnostics';

import {
  WorkspaceLayoutMetricOperation,
} from './workspace-layout-metrics';

import {
  WorkspaceLayoutTelemetry,
} from './workspace-layout-telemetry';

import {
  WorkspaceLayoutTracing,
} from './workspace-layout-tracing';

/**
 * Infraestrutura institucional responsável pela coordenação
 * da observabilidade do Workspace Layout.
 *
 * Esta infraestrutura centraliza:
 *
 * - tracing;
 * - métricas;
 * - telemetria;
 * - diagnósticos.
 *
 * Permanecendo completamente independente do Workspace Runtime,
 * Angular, mecanismos de persistência e renderização.
 */
export class WorkspaceLayoutObservability
  implements WorkspaceLayoutDiagnostics {

  /**
   * Infraestrutura institucional de telemetria.
   */
  readonly telemetry = new WorkspaceLayoutTelemetry();

  /**
   * Infraestrutura institucional de tracing.
   */
  readonly tracing = new WorkspaceLayoutTracing(
    this.telemetry,
  );

  /**
   * Estado atual da infraestrutura.
   */
  private hasActiveSession = false;

  /**
   * Quantidade de estados disponíveis para Undo.
   */
  private historySize = 0;

  /**
   * Quantidade de estados disponíveis para Redo.
   */
  private redoHistorySize = 0;

  /**
   * Atualiza o estado observado do Controller.
   */
  update(
    hasActiveSession: boolean,
    historySize: number,
    redoHistorySize: number,
  ): void {

    this.hasActiveSession = hasActiveSession;
    this.historySize = historySize;
    this.redoHistorySize = redoHistorySize;

  }

  /**
   * Obtém um snapshot institucional.
   */
  snapshot(): WorkspaceLayoutDiagnosticSnapshot {

    return {
      hasActiveSession: this.hasActiveSession,
      historySize: this.historySize,
      redoHistorySize: this.redoHistorySize,
      metrics: this.telemetry.getSummaries(),
    };

  }

  /**
   * Executa uma operação instrumentada.
   */
  trace<T>(
    operation: WorkspaceLayoutMetricOperation,
    action: () => Promise<T>,
  ): Promise<T> {

    return this.tracing.trace(
      operation,
      action,
    );

  }

  /**
   * Registra uma operação rejeitada.
   */
  rejected(
    operation: WorkspaceLayoutMetricOperation,
    startedAt: number,
  ): void {

    this.tracing.rejected(
      operation,
      startedAt,
    );

  }

}