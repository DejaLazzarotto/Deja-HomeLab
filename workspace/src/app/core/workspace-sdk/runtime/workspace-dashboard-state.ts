/*
 * Deja Workspace UI SDK
 *
 * Workspace Dashboard State
 *
 * Estado institucional responsável pela publicação do
 * Workspace Dashboard atualmente renderizado.
 */

import {
  WorkspaceLayoutMutationOperation,
} from './workspace-layout-mutation';

import {
  WorkspaceResolvedDashboard,
} from './workspace-resolved-dashboard';

/**
 * Representa uma atualização institucional do Dashboard.
 */
export interface WorkspaceDashboardUpdate {

  /**
   * Dashboard corrente.
   */
  readonly dashboard: WorkspaceResolvedDashboard;

  /**
   * Mutação concreta que originou a atualização.
   *
   * Undefined indica publicação inicial, restauração ou
   * atualização sem uma mutação específica.
   */
  readonly mutation?: WorkspaceLayoutMutationOperation;

}

/**
 * Callback institucional das alterações do Dashboard.
 */
export type WorkspaceDashboardStateListener =
  (update: WorkspaceDashboardUpdate) => void;

/**
 * Função responsável pelo cancelamento da inscrição.
 */
export type WorkspaceDashboardStateUnsubscribe =
  () => void;

/**
 * Estado institucional do Dashboard.
 */
export class WorkspaceDashboardState {

  private currentDashboard?: WorkspaceResolvedDashboard;

  private listeners =
    new Set<WorkspaceDashboardStateListener>();

  /**
   * Publica um novo estado do Dashboard.
   */
  publish(
    dashboard: WorkspaceResolvedDashboard,
    mutation?: WorkspaceLayoutMutationOperation,
  ): void {

    this.currentDashboard = dashboard;

    const update: WorkspaceDashboardUpdate = {
      dashboard,
      mutation,
    };

    for (const listener of this.listeners) {

      listener(update);

    }

  }

  /**
   * Retorna o Dashboard corrente.
   */
  current(): WorkspaceResolvedDashboard | undefined {

    return this.currentDashboard;

  }

  /**
   * Inscreve um observador.
   */
  subscribe(
    listener: WorkspaceDashboardStateListener,
  ): WorkspaceDashboardStateUnsubscribe {

    this.listeners.add(listener);

    if (this.currentDashboard) {

      listener({
        dashboard: this.currentDashboard,
      });

    }

    return () => {

      this.listeners.delete(listener);

    };

  }

  /**
   * Limpa o Dashboard corrente.
   */
  clear(): void {

    this.currentDashboard = undefined;

  }

}