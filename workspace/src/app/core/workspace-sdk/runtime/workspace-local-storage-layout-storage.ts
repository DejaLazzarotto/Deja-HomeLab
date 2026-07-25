/*
 * Deja Workspace UI SDK
 *
 * Workspace LocalStorage Layout Storage
 *
 * Implementação institucional de referência para persistência
 * de Layouts utilizando LocalStorage.
 */

import {
  WorkspaceDashboardId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceLayoutState,
} from './workspace-layout-state';

import {
  WorkspaceLayoutStorage,
} from './workspace-layout-storage';

/**
 * Implementação institucional baseada em LocalStorage.
 *
 * Esta implementação possui apenas finalidade de referência,
 * permitindo que aplicações substituam facilmente o mecanismo
 * de persistência por IndexedDB, REST, Electron, SQLite ou
 * qualquer outro backend.
 */
export class WorkspaceLocalStorageLayoutStorage
  implements WorkspaceLayoutStorage {

  /**
   * Prefixo institucional utilizado nas chaves.
   */
  constructor(
    private readonly prefix = 'workspace.layout',
  ) {}

  /**
   * Carrega um Layout persistido.
   */
  async load(
    dashboardId: WorkspaceDashboardId,
  ): Promise<WorkspaceLayoutState | undefined> {

    const json = globalThis.localStorage.getItem(
      this.key(dashboardId),
    );

    if (!json) {
      return undefined;
    }

    return JSON.parse(json) as WorkspaceLayoutState;

  }

  /**
   * Persiste um Layout.
   */
  async save(
    state: WorkspaceLayoutState,
  ): Promise<void> {

    globalThis.localStorage.setItem(
      this.key(state.dashboardId),
      JSON.stringify(state),
    );

  }

  /**
   * Remove um Layout persistido.
   */
  async remove(
    dashboardId: WorkspaceDashboardId,
  ): Promise<void> {

    globalThis.localStorage.removeItem(
      this.key(dashboardId),
    );

  }

  /**
   * Verifica a existência de um Layout.
   */
  async exists(
    dashboardId: WorkspaceDashboardId,
  ): Promise<boolean> {

    return globalThis.localStorage.getItem(
      this.key(dashboardId),
    ) !== null;

  }

  /**
   * Produz a chave institucional utilizada pelo LocalStorage.
   */
  private key(
    dashboardId: WorkspaceDashboardId,
  ): string {

    return `${this.prefix}.${dashboardId}`;

  }

}