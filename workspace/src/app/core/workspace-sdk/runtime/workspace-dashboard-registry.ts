/*
 * Deja Workspace UI SDK
 *
 * Workspace Dashboard Registry
 *
 * Registry oficial responsável pelo gerenciamento dos Dashboards
 * institucionais do Workspace.
 */

import {
  WorkspaceDashboardId,
  WorkspaceWidgetId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceDashboard,
} from './workspace-dashboard';

/**
 * Erro lançado quando um Dashboard duplicado é registrado.
 */
export class WorkspaceDashboardDuplicateError extends Error {

  constructor(readonly dashboardId: WorkspaceDashboardId) {

    super(`Workspace dashboard already registered: ${dashboardId}`);

    this.name = 'WorkspaceDashboardDuplicateError';
  }

}

/**
 * Erro lançado quando um Dashboard não existe.
 */
export class WorkspaceDashboardNotFoundError extends Error {

  constructor(readonly dashboardId: WorkspaceDashboardId) {

    super(`Workspace dashboard not found: ${dashboardId}`);

    this.name = 'WorkspaceDashboardNotFoundError';
  }

}

/**
 * Registry institucional de Workspace Dashboards.
 */
export class WorkspaceDashboardRegistry {

  private readonly dashboards =
    new Map<WorkspaceDashboardId, WorkspaceDashboard>();

  /**
   * Registra um Dashboard.
   */
  register(
    dashboard: WorkspaceDashboard,
  ): void {

    if (this.dashboards.has(dashboard.id)) {
      throw new WorkspaceDashboardDuplicateError(dashboard.id);
    }

    this.dashboards.set(dashboard.id, dashboard);

  }

  /**
   * Registra múltiplos Dashboards.
   */
  registerMany(
    dashboards: readonly WorkspaceDashboard[],
  ): void {

    dashboards.forEach((dashboard) => this.register(dashboard));

  }

  /**
   * Remove um Dashboard.
   */
  unregister(
    dashboardId: WorkspaceDashboardId,
  ): boolean {

    return this.dashboards.delete(dashboardId);

  }

  /**
   * Remove todos os Dashboards.
   */
  clear(): void {

    this.dashboards.clear();

  }

  /**
   * Obtém um Dashboard.
   */
  get(
    dashboardId: WorkspaceDashboardId,
  ): WorkspaceDashboard {

    const dashboard = this.dashboards.get(dashboardId);

    if (!dashboard) {
      throw new WorkspaceDashboardNotFoundError(dashboardId);
    }

    return dashboard;

  }

  /**
   * Verifica se um Dashboard existe.
   */
  has(
    dashboardId: WorkspaceDashboardId,
  ): boolean {

    return this.dashboards.has(dashboardId);

  }

  /**
   * Retorna todos os Dashboards.
   */
  getAll(): readonly WorkspaceDashboard[] {

    return [...this.dashboards.values()];

  }

  /**
   * Retorna Dashboards habilitados.
   */
  getEnabled(): readonly WorkspaceDashboard[] {

    return this.getAll().filter(
      (dashboard) => dashboard.enabled !== false,
    );

  }

  /**
   * Consulta Dashboards por Widget.
   */
  getByWidget(
    widgetId: WorkspaceWidgetId,
  ): readonly WorkspaceDashboard[] {

    return this.getAll().filter(
      (dashboard) => dashboard.widgets?.some(
        (widget) => widget.widgetId === widgetId,
      ),
    );

  }

  /**
   * Consulta Dashboards por rota.
   */
  getByRoute(
    route: string,
  ): readonly WorkspaceDashboard[] {

    return this.getAll().filter(
      (dashboard) => dashboard.route === route,
    );

  }

  /**
   * Consulta Dashboards por tag.
   */
  getByTag(
    tag: string,
  ): readonly WorkspaceDashboard[] {

    return this.getAll().filter(
      (dashboard) => dashboard.tags?.includes(tag),
    );

  }

  /**
   * Quantidade de Dashboards registrados.
   */
  size(): number {

    return this.dashboards.size;

  }

}