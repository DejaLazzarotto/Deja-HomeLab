/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Persistence
 *
 * Infraestrutura institucional responsável pela coordenação
 * entre estados resolvidos de Dashboard e mecanismos externos
 * de persistência de Layout.
 */

import {
  WorkspaceDashboardId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceLayoutStateMapper,
} from './workspace-layout-state-mapper';

import {
  WorkspaceLayoutStorage,
} from './workspace-layout-storage';

import {
  WorkspaceResolvedDashboard,
} from './workspace-resolved-dashboard';

/**
 * Coordena a persistência institucional de Layouts.
 *
 * Esta infraestrutura permanece independente:
 *
 * - do mecanismo concreto de armazenamento;
 * - da tecnologia de renderização;
 * - do Workspace Runtime;
 * - do Workspace Layout Mutator;
 * - do Workspace Dashboard Resolver.
 */
export class WorkspaceLayoutPersistence {

  constructor(
    private readonly storage: WorkspaceLayoutStorage,
  ) {}

  /**
   * Persiste o estado atual de um Dashboard resolvido.
   *
   * Retorna false quando o Dashboard não possui informações
   * suficientes para produzir um estado persistível.
   */
  async save(
    dashboard: WorkspaceResolvedDashboard,
  ): Promise<boolean> {

    const state =
      WorkspaceLayoutStateMapper.fromResolvedDashboard(
        dashboard,
      );

    if (!state) {
      return false;
    }

    await this.storage.save(state);

    return true;
  }

  /**
   * Carrega e aplica o estado persistido de um Dashboard.
   *
   * Quando nenhum estado estiver armazenado, o Dashboard
   * recebido será preservado integralmente.
   */
  async restore(
    dashboard: WorkspaceResolvedDashboard,
  ): Promise<WorkspaceResolvedDashboard> {

    const state = await this.storage.load(
      dashboard.dashboard.id,
    );

    if (!state) {
      return dashboard;
    }

    return WorkspaceLayoutStateMapper.applyState(
      dashboard,
      state,
    );
  }

  /**
   * Remove o estado persistido de um Dashboard.
   */
  async remove(
    dashboardId: WorkspaceDashboardId,
  ): Promise<void> {

    await this.storage.remove(dashboardId);

  }

  /**
   * Verifica se existe estado persistido para um Dashboard.
   */
  async exists(
    dashboardId: WorkspaceDashboardId,
  ): Promise<boolean> {

    return this.storage.exists(dashboardId);

  }

}