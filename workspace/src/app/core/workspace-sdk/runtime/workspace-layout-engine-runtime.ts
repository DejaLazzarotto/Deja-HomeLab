/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Engine Runtime
 *
 * Implementação institucional responsável pela resolução lógica
 * dos Layouts utilizados pelos Dashboards do Workspace.
 */

import {
  WorkspaceDashboardId,
  WorkspaceDashboardLayoutId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceRegistries,
} from '../registries/workspace-registries';

import {
  WorkspaceDashboard,
} from './workspace-dashboard';

import {
  WorkspaceLayout,
} from './workspace-layout';

import {
  WorkspaceLayoutEngine,
} from './workspace-layout-engine';

import {
  WorkspaceLayoutState,
} from './workspace-layout-state';

import {
  WorkspaceLayoutStorage,
} from './workspace-layout-storage';

/**
 * Implementação institucional do Workspace Layout Engine.
 *
 * Responsabilidades:
 *
 * - localizar Layouts registrados;
 * - resolver o Layout associado a um Dashboard;
 * - validar referências entre Dashboards e Layouts;
 * - carregar estado persistido;
 * - persistir estado de Layout;
 * - permanecer independente de Angular e renderização.
 */
export class WorkspaceLayoutEngineRuntime
  implements WorkspaceLayoutEngine {

  /**
   * Cria uma nova instância do Layout Engine.
   *
   * O mecanismo de armazenamento é opcional para permitir
   * a utilização do Layout Engine sem persistência.
   */
  constructor(
    private readonly registries: WorkspaceRegistries,
    private readonly storage?: WorkspaceLayoutStorage,
  ) {}

  /**
   * Obtém um Layout pelo seu identificador.
   */
  getLayout(
    layoutId: WorkspaceDashboardLayoutId,
  ): WorkspaceLayout | undefined {
    return this.registries.layouts.get(layoutId);
  }

  /**
   * Obtém o Layout associado a um Dashboard.
   *
   * Retorna undefined quando:
   *
   * - o Dashboard não possui Layout associado;
   * - o Layout não está registrado;
   * - o Layout está desabilitado.
   */
  resolveLayout(
    dashboard: WorkspaceDashboard,
  ): WorkspaceLayout | undefined {
    if (!dashboard.layoutId) {
      return undefined;
    }

    const layout = this.getLayout(dashboard.layoutId);

    if (!layout || layout.enabled === false) {
      return undefined;
    }

    return layout;
  }

  /**
   * Carrega o estado persistido de um Dashboard.
   *
   * Quando nenhum mecanismo de armazenamento estiver configurado,
   * retorna undefined.
   */
  async loadState(
    dashboardId: WorkspaceDashboardId,
  ): Promise<WorkspaceLayoutState | undefined> {
    if (!this.storage) {
      return undefined;
    }

    return this.storage.load(dashboardId);
  }

  /**
   * Persiste o estado atual de um Dashboard.
   *
   * Quando nenhum mecanismo de armazenamento estiver configurado,
   * a operação é ignorada.
   */
  async saveState(
    state: WorkspaceLayoutState,
  ): Promise<void> {
    if (!this.storage) {
      return;
    }

    await this.storage.save(state);
  }

  /**
   * Verifica se o Dashboard possui uma referência válida
   * para um Layout registrado e habilitado.
   *
   * Dashboards sem layoutId são considerados válidos para
   * preservar compatibilidade com Dashboards legados.
   */
  validate(
    dashboard: WorkspaceDashboard,
  ): boolean {
    if (!dashboard.layoutId) {
      return true;
    }

    const layout = this.getLayout(dashboard.layoutId);

    return layout !== undefined && layout.enabled !== false;
  }
}