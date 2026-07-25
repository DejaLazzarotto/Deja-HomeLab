/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Session
 *
 * Infraestrutura institucional responsável pela representação
 * de uma sessão de trabalho sobre um Dashboard resolvido.
 */

import {
  WorkspaceLayoutMutationOperation,
  WorkspaceLayoutMutationResult,
} from './workspace-layout-mutation';

import {
  WorkspaceLayoutMutator,
} from './workspace-layout-mutator';

import {
  WorkspaceLayoutPersistence,
} from './workspace-layout-persistence';

import {
  WorkspaceResolvedDashboard,
} from './workspace-resolved-dashboard';

/**
 * Erro lançado quando uma operação é executada sobre uma
 * Workspace Layout Session encerrada.
 */
export class WorkspaceLayoutSessionClosedError extends Error {

  constructor() {

    super('Workspace layout session is closed.');

    this.name = 'WorkspaceLayoutSessionClosedError';

  }

}

/**
 * Representa uma sessão institucional de trabalho sobre
 * um Workspace Dashboard resolvido.
 *
 * A sessão coordena:
 *
 * - o estado corrente do Dashboard;
 * - a restauração do estado persistido;
 * - a aplicação de mutações estruturadas;
 * - a persistência automática de alterações aprovadas;
 * - o histórico de estados anteriores;
 * - o histórico de estados disponíveis para Redo;
 * - operações institucionais de Undo e Redo.
 *
 * A sessão permanece independente:
 *
 * - do Workspace Runtime;
 * - da tecnologia de renderização;
 * - de Angular;
 * - de mecanismos concretos de armazenamento;
 * - de Auto Save temporizado;
 * - de sincronização externa.
 */
export class WorkspaceLayoutSession {

  private currentDashboard: WorkspaceResolvedDashboard;

  /**
   * Estados anteriores disponíveis para Undo.
   */
  private readonly history: WorkspaceResolvedDashboard[] = [];

  /**
   * Estados futuros disponíveis para Redo.
   */
  private readonly redoHistory: WorkspaceResolvedDashboard[] = [];

  private closed = false;

  constructor(
    dashboard: WorkspaceResolvedDashboard,
    private readonly persistence: WorkspaceLayoutPersistence,
  ) {

    this.currentDashboard = dashboard;

  }

  /**
   * Dashboard atualmente mantido pela sessão.
   */
  get dashboard(): WorkspaceResolvedDashboard {

    return this.currentDashboard;

  }

  /**
   * Quantidade de estados disponíveis para Undo.
   */
  get historySize(): number {

    return this.history.length;

  }

  /**
   * Quantidade de estados disponíveis para Redo.
   */
  get redoHistorySize(): number {

    return this.redoHistory.length;

  }

  /**
   * Indica se existe um estado anterior disponível para Undo.
   */
  get canUndo(): boolean {

    return this.history.length > 0;

  }

  /**
   * Indica se existe um estado futuro disponível para Redo.
   */
  get canRedo(): boolean {

    return this.redoHistory.length > 0;

  }

  /**
   * Indica se a sessão permanece aberta.
   */
  get isOpen(): boolean {

    return !this.closed;

  }

  /**
   * Indica se a sessão foi encerrada.
   */
  get isClosed(): boolean {

    return this.closed;

  }

  /**
   * Restaura o estado persistido do Dashboard e atualiza
   * o estado corrente da sessão.
   *
   * A restauração estabelece uma nova referência inicial para
   * a sessão e, portanto, descarta os históricos de Undo e Redo.
   */
  async restore(): Promise<WorkspaceResolvedDashboard> {

    this.assertOpen();

    this.currentDashboard =
      await this.persistence.restore(
        this.currentDashboard,
      );

    this.clearHistory();

    return this.currentDashboard;

  }

  /**
   * Aplica uma mutação estrutural ao Dashboard corrente.
   *
   * Quando a mutação for aprovada:
   *
   * - o Dashboard corrente será armazenado no histórico de Undo;
   * - o histórico de Redo será descartado;
   * - o Dashboard resultante se tornará o estado corrente;
   * - o novo estado será persistido automaticamente.
   *
   * Quando a mutação for rejeitada, nenhum estado ou histórico
   * será alterado e nenhuma persistência será executada.
   */
  async mutate(
    mutation: WorkspaceLayoutMutationOperation,
  ): Promise<WorkspaceLayoutMutationResult> {

    this.assertOpen();

    const result = WorkspaceLayoutMutator.mutate(
      this.currentDashboard,
      mutation,
    );

    if (!result.applied) {
      return result;
    }

    this.history.push(
      this.currentDashboard,
    );

    this.redoHistory.length = 0;

    this.currentDashboard = result.dashboard;

    await this.persistence.save(
      this.currentDashboard,
    );

    return result;

  }

  /**
   * Restaura o último estado anterior disponível na sessão.
   *
   * O estado corrente será preservado no histórico de Redo antes
   * da restauração do estado anterior.
   *
   * Quando não existir histórico disponível, nenhuma alteração
   * será realizada e false será retornado.
   */
  async undo(): Promise<boolean> {

    this.assertOpen();

    const previousDashboard = this.history.pop();

    if (!previousDashboard) {
      return false;
    }

    this.redoHistory.push(
      this.currentDashboard,
    );

    this.currentDashboard = previousDashboard;

    await this.persistence.save(
      this.currentDashboard,
    );

    return true;

  }

  /**
   * Restaura o próximo estado disponível no histórico de Redo.
   *
   * O estado corrente será preservado no histórico de Undo antes
   * da restauração do estado futuro.
   *
   * Quando não existir estado disponível para Redo, nenhuma
   * alteração será realizada e false será retornado.
   */
  async redo(): Promise<boolean> {

    this.assertOpen();

    const nextDashboard = this.redoHistory.pop();

    if (!nextDashboard) {
      return false;
    }

    this.history.push(
      this.currentDashboard,
    );

    this.currentDashboard = nextDashboard;

    await this.persistence.save(
      this.currentDashboard,
    );

    return true;

  }

  /**
   * Encerra a sessão.
   *
   * Todos os históricos internos serão descartados e nenhuma
   * persistência adicional será executada.
   */
  close(): void {

    this.clearHistory();

    this.closed = true;

  }

  /**
   * Descarta todos os estados mantidos pelos históricos
   * institucionais da sessão.
   */
  private clearHistory(): void {

    this.history.length = 0;
    this.redoHistory.length = 0;

  }

  /**
   * Garante que a sessão permanece aberta antes da execução
   * de operações institucionais.
   */
  private assertOpen(): void {

    if (this.closed) {
      throw new WorkspaceLayoutSessionClosedError();
    }

  }

}
