/*
 * Deja Workspace Angular Integration
 *
 * Workspace Shell Controller
 *
 * Controlador institucional responsável por orquestrar o ciclo
 * de vida visual do Workspace.
 *
 * Estabelece a ligação entre o Workspace Runtime e a camada
 * Angular de apresentação, preservando o desacoplamento entre
 * o Workspace SDK e o framework.
 */

import { Injectable } from '@angular/core';

import {
  WorkspaceDashboardId,
  WorkspaceNavigationId,
} from '../../core/workspace-sdk/contracts/workspace-contracts';

import { WorkspaceDashboardResolver } from '../../core/workspace-sdk/runtime/workspace-dashboard-resolver';

import { WorkspaceRenderContext } from '../../core/workspace-sdk/runtime/workspace-render-context';

import { WorkspaceResolvedDashboard } from '../../core/workspace-sdk/runtime/workspace-resolved-dashboard';

import { WorkspaceRuntime } from '../../core/workspace-sdk/runtime/workspace-runtime';

import { WorkspaceBootstrapService } from '../bootstrap/workspace-bootstrap.service';

import { AngularWorkspaceRenderHost } from '../rendering/angular-workspace-render-host';

/**
 * Erro lançado quando o Workspace Runtime não possui
 * um Layout Engine configurado.
 */
export class WorkspaceShellLayoutEngineNotAvailableError extends Error {
  constructor() {
    super('Workspace Shell requires a configured Workspace Layout Engine.');

    this.name = 'WorkspaceShellLayoutEngineNotAvailableError';
  }
}

/**
 * Erro lançado quando não existe nenhum Dashboard habilitado
 * para a inicialização visual do Workspace.
 */
export class WorkspaceShellDashboardNotAvailableError extends Error {
  constructor() {
    super('No enabled Workspace Dashboard is available for initial rendering.');

    this.name = 'WorkspaceShellDashboardNotAvailableError';
  }
}

/**
 * Controlador oficial da Workspace Shell.
 */
@Injectable({
  providedIn: 'root',
})
export class WorkspaceShellController {
  /**
   * Contexto atualmente utilizado pela renderização.
   */
  private renderContext?: WorkspaceRenderContext;

  /**
   * Dashboard atualmente apresentado pela Shell.
   */
  private currentDashboard?: WorkspaceResolvedDashboard;

  /**
   * Indica se a camada visual da Shell está ativa.
   */
  private active = false;

  constructor(private readonly bootstrap: WorkspaceBootstrapService) {}

  /**
   * Retorna o Runtime oficial associado à Shell.
   */
  getRuntime(): WorkspaceRuntime {
    return this.bootstrap.getRuntime();
  }

  /**
   * Retorna o Dashboard atualmente apresentado.
   */
  getCurrentDashboard(): WorkspaceResolvedDashboard | undefined {
    return this.currentDashboard;
  }

  /**
   * Indica se a Shell está visualmente ativa.
   */
  isActive(): boolean {
    return this.active;
  }

  /**
   * Inicia a camada visual do Workspace.
   *
   * Quando nenhum identificador é informado, o primeiro
   * Dashboard habilitado segundo a ordenação institucional
   * do registry é utilizado.
   */
  async start(host: AngularWorkspaceRenderHost, dashboardId?: WorkspaceDashboardId): Promise<void> {
    const runtime = this.getRuntime();

    const dashboard = await this.resolveInitialDashboard(runtime, dashboardId);

    const context: WorkspaceRenderContext = {
      technology: 'angular',
      host,
    };

    await runtime.renderDashboard(dashboard, context);

    this.renderContext = context;
    this.currentDashboard = dashboard;
    this.active = true;
  }

  /**
   * Navega e apresenta o Dashboard resolvido na área central.
   */
  async navigate(
    navigationId: WorkspaceNavigationId,
  ): Promise<void> {

    if (!this.renderContext) {
      throw new Error(
        'Workspace Shell is not ready for navigation.',
      );
    }

    const runtime = this.getRuntime();

    const result = await runtime.navigate(
      navigationId,
    );

    await runtime.renderDashboard(
      result.dashboard,
      this.renderContext,
    );

    this.currentDashboard = result.dashboard;

    if (
      window.location.pathname
      !== result.dashboard.dashboard.route
    ) {
      window.history.pushState(
        {},
        '',
        result.dashboard.dashboard.route,
      );
    }

  }

  /**
   * Encerra a camada visual do Workspace.
   */
  async stop(): Promise<void> {
    if (!this.renderContext) {
      this.currentDashboard = undefined;
      this.active = false;

      return;
    }

    await this.getRuntime().disposeRenderer(this.renderContext);

    this.renderContext = undefined;
    this.currentDashboard = undefined;
    this.active = false;
  }

  /**
   * Resolve o Dashboard que será inicialmente apresentado.
   */
  private async resolveInitialDashboard(
    runtime: WorkspaceRuntime,
    dashboardId?: WorkspaceDashboardId,
  ): Promise<WorkspaceResolvedDashboard> {
    const layoutEngine = runtime.getLayoutEngine();

    if (!layoutEngine) {
      throw new WorkspaceShellLayoutEngineNotAvailableError();
    }

    const resolver = new WorkspaceDashboardResolver(runtime.registries, layoutEngine);

    if (dashboardId) {
      return resolver.resolve(dashboardId);
    }

       const dashboards =
      runtime.registries.dashboards.list({
        enabled: true,
      });

    const routeDashboard = dashboards.find(
      dashboard => (
        dashboard.route
        === window.location.pathname
      ),
    );

    const dashboard =
      routeDashboard
      ?? dashboards[0];

    if (!dashboard) {
      throw new WorkspaceShellDashboardNotAvailableError();
    }

    return resolver.resolveDashboard(
      dashboard,
    );
  }
}
