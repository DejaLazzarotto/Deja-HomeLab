/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Metrics
 *
 * Contratos institucionais responsáveis pela representação
 * das métricas operacionais do Workspace Layout.
 */

/**
 * Operações institucionais observáveis executadas pelo
 * Workspace Layout Controller.
 */
export type WorkspaceLayoutMetricOperation =
  | 'session.open'
  | 'session.close'
  | 'layout.restore'
  | 'layout.mutate'
  | 'layout.undo'
  | 'layout.redo';

/**
 * Resultado institucional de uma operação observada.
 */
export type WorkspaceLayoutMetricOutcome =
  | 'succeeded'
  | 'rejected'
  | 'failed';

/**
 * Registro individual de uma operação observada.
 */
export interface WorkspaceLayoutMetricRecord {

  /**
   * Operação executada.
   */
  readonly operation: WorkspaceLayoutMetricOperation;

  /**
   * Resultado final da operação.
   */
  readonly outcome: WorkspaceLayoutMetricOutcome;

  /**
   * Duração total da operação em milissegundos.
   */
  readonly duration: number;

  /**
   * Instante em que a operação foi concluída.
   */
  readonly timestamp: number;

}

/**
 * Resumo agregado das métricas de uma operação.
 */
export interface WorkspaceLayoutMetricSummary {

  /**
   * Operação representada.
   */
  readonly operation: WorkspaceLayoutMetricOperation;

  /**
   * Quantidade total de execuções.
   */
  readonly executions: number;

  /**
   * Quantidade de execuções concluídas com sucesso.
   */
  readonly succeeded: number;

  /**
   * Quantidade de execuções rejeitadas.
   */
  readonly rejected: number;

  /**
   * Quantidade de execuções encerradas por falha.
   */
  readonly failed: number;

  /**
   * Duração total acumulada em milissegundos.
   */
  readonly totalDuration: number;

  /**
   * Duração média das execuções em milissegundos.
   */
  readonly averageDuration: number;

}

/**
 * Contrato institucional para coleta de métricas do
 * Workspace Layout.
 *
 * Implementações concretas podem armazenar métricas em memória,
 * encaminhá-las para sistemas externos ou ignorá-las completamente.
 */
export interface WorkspaceLayoutMetrics {

  /**
   * Registra a conclusão de uma operação observada.
   */
  record(record: WorkspaceLayoutMetricRecord): void;

  /**
   * Retorna o resumo agregado de uma operação.
   */
  getSummary(
    operation: WorkspaceLayoutMetricOperation,
  ): WorkspaceLayoutMetricSummary;

  /**
   * Retorna todos os resumos disponíveis.
   */
  getSummaries(): readonly WorkspaceLayoutMetricSummary[];

  /**
   * Remove todas as métricas coletadas.
   */
  clear(): void;

}