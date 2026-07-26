/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Diagnostics
 *
 * Contratos institucionais responsáveis pela exposição
 * de informações de diagnóstico do Workspace Layout.
 */

import {
  WorkspaceLayoutMetricSummary,
} from './workspace-layout-metrics';

/**
 * Estado institucional da infraestrutura de Layout.
 */
export interface WorkspaceLayoutDiagnosticSnapshot {

  /**
   * Indica se existe uma sessão ativa.
   */
  readonly hasActiveSession: boolean;

  /**
   * Quantidade de estados disponíveis para Undo.
   */
  readonly historySize: number;

  /**
   * Quantidade de estados disponíveis para Redo.
   */
  readonly redoHistorySize: number;

  /**
   * Resumos das métricas coletadas.
   */
  readonly metrics: readonly WorkspaceLayoutMetricSummary[];

}

/**
 * Contrato institucional responsável pela obtenção de
 * diagnósticos do Workspace Layout.
 *
 * Implementações permanecem independentes da tecnologia
 * de renderização, do mecanismo de persistência e do
 * Workspace Runtime.
 */
export interface WorkspaceLayoutDiagnostics {

  /**
   * Obtém um snapshot consistente do estado atual da
   * infraestrutura de Layout.
   */
  snapshot(): WorkspaceLayoutDiagnosticSnapshot;

}