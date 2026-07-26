/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Controller
 *
 * Infraestrutura institucional responsável pela coordenação
 * das sessões de edição de Layout do Workspace.
 */

import { WorkspaceLayoutEventDispatcher } from './workspace-layout-event-dispatcher';

import {
  createWorkspaceLayoutMutatedEvent,
  createWorkspaceLayoutRedoExecutedEvent,
  createWorkspaceLayoutRestoredEvent,
  createWorkspaceLayoutSessionClosedEvent,
  createWorkspaceLayoutSessionOpenedEvent,
  createWorkspaceLayoutUndoExecutedEvent,
} from './workspace-layout-event-builders';

import { WorkspaceLayoutExtensionDispatcher } from './workspace-layout-extension-dispatcher';

import { WorkspaceLayoutHookDispatcher } from './workspace-layout-hook-dispatcher';

import {
  WorkspaceLayoutMutationOperation,
  WorkspaceLayoutMutationResult,
} from './workspace-layout-mutation';

import { WorkspaceLayoutPersistence } from './workspace-layout-persistence';

import { WorkspaceLayoutSession } from './workspace-layout-session';

import { WorkspaceResolvedDashboard } from './workspace-resolved-dashboard';

import { WorkspaceLayoutObservability } from './workspace-layout-observability';

/**
 * Erro lançado quando uma nova sessão é aberta enquanto
 * outra Workspace Layout Session permanece ativa.
 */
export class WorkspaceLayoutControllerSessionAlreadyOpenError extends Error {
  constructor() {
    super('A workspace layout session is already open.');

    this.name = 'WorkspaceLayoutControllerSessionAlreadyOpenError';
  }
}

/**
 * Erro lançado quando uma operação institucional é executada
 * sem que exista uma Workspace Layout Session ativa.
 */
export class WorkspaceLayoutControllerSessionNotOpenError extends Error {
  constructor() {
    super('No workspace layout session is open.');

    this.name = 'WorkspaceLayoutControllerSessionNotOpenError';
  }
}

/**
 * Coordena institucionalmente as sessões de edição de Layout.
 *
 * O Controller representa o ponto único de acesso externo às
 * operações de edição, ocultando completamente a infraestrutura
 * interna da Workspace Layout Session.
 *
 * O Controller permanece independente:
 *
 * - do Workspace Runtime;
 * - do Workspace Dashboard Resolver;
 * - do Workspace Layout Mutator;
 * - do mecanismo concreto de armazenamento;
 * - da tecnologia de renderização;
 * - de Angular;
 * - de Electron.
 */
export class WorkspaceLayoutController {
  private activeSession?: WorkspaceLayoutSession;

  constructor(
    private readonly persistence: WorkspaceLayoutPersistence,
    private readonly events: WorkspaceLayoutEventDispatcher,
    private readonly hooks: WorkspaceLayoutHookDispatcher,
    private readonly extensions: WorkspaceLayoutExtensionDispatcher,
    private readonly observability: WorkspaceLayoutObservability,
  ) {}

  /**
   * Dashboard atualmente mantido pela sessão ativa.
   *
   * Retorna undefined quando nenhuma sessão estiver aberta.
   */
  get dashboard(): WorkspaceResolvedDashboard | undefined {
    return this.activeSession?.dashboard;
  }

  /**
   * Indica se existe uma sessão ativa.
   */
  get hasActiveSession(): boolean {
    return this.activeSession !== undefined;
  }

  /**
   * Indica se existe um estado anterior disponível para Undo.
   */
  get canUndo(): boolean {
    return this.activeSession?.canUndo ?? false;
  }

  /**
   * Indica se existe um estado futuro disponível para Redo.
   */
  get canRedo(): boolean {
    return this.activeSession?.canRedo ?? false;
  }

  /**
   * Quantidade de estados disponíveis para Undo.
   */
  get historySize(): number {
    return this.activeSession?.historySize ?? 0;
  }

  /**
   * Quantidade de estados disponíveis para Redo.
   */
  get redoHistorySize(): number {
    return this.activeSession?.redoHistorySize ?? 0;
  }

  /**
   * Abre uma nova sessão institucional de edição.
   *
   * Apenas uma sessão pode permanecer ativa por Controller.
   */
  async open(dashboard: WorkspaceResolvedDashboard): Promise<WorkspaceResolvedDashboard> {
    return this.observability.trace('session.open', async () => {
      if (this.activeSession) {
        throw new WorkspaceLayoutControllerSessionAlreadyOpenError();
      }

      await this.hooks.dispatch('beforeSessionOpen', undefined);

      await this.extensions.dispatch('workspace.layout.session.opening', dashboard);

      const session = new WorkspaceLayoutSession(dashboard, this.persistence);

      this.activeSession = session;

      this.observability.update(this.hasActiveSession, this.historySize, this.redoHistorySize);

      const currentDashboard = session.dashboard;

      this.events.dispatch(createWorkspaceLayoutSessionOpenedEvent(currentDashboard));

      await this.extensions.dispatch('workspace.layout.session.opened', session);

      await this.hooks.dispatch('afterSessionOpen', session);

      return currentDashboard;
    });
  }

  /**
   * Encerra a sessão ativa.
   *
   * Quando nenhuma sessão estiver aberta, nenhuma operação
   * adicional será realizada.
   */
  async close(): Promise<void> {
    if (!this.activeSession) {
      return;
    }

    const session = this.activeSession;

    await this.hooks.dispatch('beforeSessionClose', session);

    await this.extensions.dispatch('workspace.layout.session.closing', session);

    const dashboard = session.dashboard;

    session.close();

    this.activeSession = undefined;

    this.observability.update(this.hasActiveSession, this.historySize, this.redoHistorySize);

    await this.extensions.dispatch('workspace.layout.session.closed', dashboard);

    await this.hooks.dispatch('afterSessionClose', undefined);
  }

  /**
   * Restaura o estado persistido do Dashboard mantido pela
   * sessão ativa.
   */
  async restore(): Promise<WorkspaceResolvedDashboard> {
    const session = this.getActiveSession();

    await this.hooks.dispatch('beforeRestore', session);

    await this.extensions.dispatch('workspace.layout.restoring', session);

    const dashboard = await session.restore();

    this.events.dispatch(createWorkspaceLayoutRestoredEvent(dashboard));

    await this.extensions.dispatch('workspace.layout.restored', dashboard);

    await this.hooks.dispatch('afterRestore', session);

    return dashboard;
  }

  /**
   * Aplica uma mutação estrutural ao Dashboard mantido pela
   * sessão ativa.
   */
  async mutate(mutation: WorkspaceLayoutMutationOperation): Promise<WorkspaceLayoutMutationResult> {
    const session = this.getActiveSession();

    await this.hooks.dispatch('beforeMutation', session);

    await this.extensions.dispatch('workspace.layout.mutating', {
      session,
      mutation,
    });

    const result = await session.mutate(mutation);

    if (!result.applied) {
      return result;
    }

    this.observability.update(this.hasActiveSession, this.historySize, this.redoHistorySize);

    this.events.dispatch(createWorkspaceLayoutMutatedEvent(mutation, result, session.dashboard));

    await this.extensions.dispatch('workspace.layout.mutated', {
      session,
      mutation,
      result,
    });

    await this.hooks.dispatch('afterMutation', result);

    return result;
  }

  /**
   * Restaura o último estado anterior disponível na
   * sessão ativa.
   */
  async undo(): Promise<boolean> {
    const session = this.getActiveSession();

    await this.hooks.dispatch('beforeUndo', session);

    await this.extensions.dispatch('workspace.layout.undoing', session);

    const executed = await session.undo();

    if (!executed) {
      return false;
    }

    this.observability.update(this.hasActiveSession, this.historySize, this.redoHistorySize);

    this.events.dispatch(createWorkspaceLayoutUndoExecutedEvent(session.dashboard));

    await this.extensions.dispatch('workspace.layout.undone', session);

    await this.hooks.dispatch('afterUndo', session);

    return true;
  }

  /**
   * Restaura o próximo estado disponível no histórico de
   * Redo da sessão ativa.
   */
  async redo(): Promise<boolean> {
    const session = this.getActiveSession();

    await this.hooks.dispatch('beforeRedo', session);

    await this.extensions.dispatch('workspace.layout.redoing', session);

    const executed = await session.redo();

    if (!executed) {
      return false;
    }

    this.observability.update(this.hasActiveSession, this.historySize, this.redoHistorySize);

    this.events.dispatch(createWorkspaceLayoutRedoExecutedEvent(session.dashboard));

    await this.extensions.dispatch('workspace.layout.redone', session);

    await this.hooks.dispatch('afterRedo', session);

    return true;
  }

  /**
   * Obtém a sessão ativa ou interrompe a operação quando
   * nenhuma sessão estiver aberta.
   */
  private getActiveSession(): WorkspaceLayoutSession {
    if (!this.activeSession) {
      throw new WorkspaceLayoutControllerSessionNotOpenError();
    }

    return this.activeSession;
  }
}
