/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Manager
 *
 * Fachada institucional responsável pela coordenação das
 * sessões de Layout do Workspace.
 */

import {
  WorkspaceDashboardState,
} from './workspace-dashboard-state';

import {
  WorkspaceLayoutController,
} from './workspace-layout-controller';

import {
  WorkspaceLayoutServices,
} from './workspace-layout-services';

import {
  WorkspaceResolvedDashboard,
} from './workspace-resolved-dashboard';

/**
 * Responsável pela coordenação institucional do
 * Workspace Layout.
 *
 * O Manager representa o ponto oficial de acesso ao
 * subsistema de Layout do Workspace Runtime.
 *
 * Suas responsabilidades incluem:
 *
 * - resolução de Dashboards;
 * - criação de Workspace Layout Controllers;
 * - gerenciamento das sessões de Layout;
 * - centralização da infraestrutura de Layout;
 * - exposição do estado corrente do Dashboard;
 * - preparação para múltiplas sessões futuras.
 *
 * Esta infraestrutura permanece independente:
 *
 * - do Angular;
 * - do mecanismo de renderização;
 * - da persistência concreta;
 * - da tecnologia de interface.
 */
export class WorkspaceLayoutManager {

  constructor(
    private readonly services: WorkspaceLayoutServices,
  ) {}

  /**
   * Estado institucional do Dashboard atualmente controlado
   * pelo subsistema de Layout.
   */
  get dashboardState(): WorkspaceDashboardState {

    return this.services.dashboardState;

  }

  /**
   * Cria um Workspace Layout Controller para um
   * Dashboard previamente resolvido.
   */
  createController(): WorkspaceLayoutController {

    return new WorkspaceLayoutController(
      this.services,
    );

  }

  /**
   * Abre uma nova sessão de edição para um Dashboard
   * previamente resolvido.
   */
  async open(
    dashboard: WorkspaceResolvedDashboard,
  ): Promise<WorkspaceLayoutController> {

    const controller = this.createController();

    await controller.open(dashboard);

    return controller;

  }

  /**
   * Encerramento institucional de uma sessão.
   */
  async close(
    controller: WorkspaceLayoutController,
  ): Promise<void> {

    await controller.close();

  }

}