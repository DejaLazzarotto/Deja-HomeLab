/*
 * Deja Workspace UI SDK
 *
 * Workspace Dashboard Resolver
 *
 * Responsável pela resolução lógica de um Dashboard,
 * produzindo um WorkspaceResolvedDashboard pronto para
 * consumo pela futura camada de renderização.
 */

import {
  WorkspaceDashboardId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceRegistries,
} from '../registries/workspace-registries';

import {
  WorkspaceDashboard,
} from './workspace-dashboard';

import {
  WorkspaceLayoutEngine,
} from './workspace-layout-engine';

import {
  WorkspaceResolvedDashboard,
} from './workspace-resolved-dashboard';

import {
  WorkspaceWidgetInstance,
} from './workspace-widget';

/**
 * Responsável pela resolução institucional de Dashboards.
 */
export class WorkspaceDashboardResolver {

  constructor(
    private readonly registries: WorkspaceRegistries,
    private readonly layoutEngine: WorkspaceLayoutEngine,
  ) {}

  /**
   * Resolve um Dashboard pelo seu identificador.
   */
  async resolve(
    dashboardId: WorkspaceDashboardId,
  ): Promise<WorkspaceResolvedDashboard> {

    const dashboard = this.registries.dashboards.require(dashboardId);

    return this.resolveDashboard(dashboard);
  }

  /**
   * Resolve um Dashboard informado.
   */
  async resolveDashboard(
    dashboard: WorkspaceDashboard,
  ): Promise<WorkspaceResolvedDashboard> {

    const diagnostics: string[] = [];

    const layout = this.layoutEngine.resolveLayout(dashboard);

    if (dashboard.layoutId && !layout) {
      diagnostics.push(
        `Layout not found: ${dashboard.layoutId}`,
      );
    }

    const state = await this.layoutEngine.loadState(
      dashboard.id,
    );

    const widgets = this.resolveWidgets(
      dashboard.widgets,
      diagnostics,
    );

    return {
      dashboard,
      layout,
      widgets,
      state,
      valid: diagnostics.length === 0,
      diagnostics,
    };
  }

  /**
   * Resolve e valida as instâncias de Widgets.
   */
  private resolveWidgets(
    widgets: readonly WorkspaceWidgetInstance[] | undefined,
    diagnostics: string[],
  ): readonly WorkspaceWidgetInstance[] {

    if (!widgets?.length) {
      return [];
    }

    const resolved: WorkspaceWidgetInstance[] = [];

    for (const widget of widgets) {

      const definition =
        this.registries.widgets.get(widget.widgetId);

      if (!definition) {
        diagnostics.push(
          `Widget not registered: ${widget.widgetId}`,
        );
        continue;
      }

      if (definition.enabled === false) {
        diagnostics.push(
          `Widget disabled: ${widget.widgetId}`,
        );
        continue;
      }

      resolved.push(widget);
    }

    return resolved;
  }
}