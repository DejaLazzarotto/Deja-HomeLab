/*
 * Deja Workspace UI SDK
 *
 * Workspace Dashboard Resolver
 *
 * Responsável pela resolução lógica de um Dashboard,
 * produzindo um WorkspaceResolvedDashboard pronto para
 * consumo pela camada de renderização.
 */

import { WorkspaceDashboardId } from '../contracts/workspace-contracts';

import { WorkspaceRegistries } from '../registries/workspace-registries';

import { WorkspaceDashboard } from './workspace-dashboard';

import { WorkspaceLayout } from './workspace-layout';

import { WorkspaceLayoutEngine } from './workspace-layout-engine';

import { WorkspaceLayoutRegion } from './workspace-layout-region';

import { WorkspaceResolvedDashboard } from './workspace-resolved-dashboard';

import { WorkspaceWidgetInstance } from './workspace-widget';

import { WorkspaceGridConfigurationResolver } from './workspace-grid-configuration-resolver';
import { WorkspaceLayoutCapabilityResolver } from './workspace-layout-capability-resolver';

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
  async resolve(dashboardId: WorkspaceDashboardId): Promise<WorkspaceResolvedDashboard> {
    const dashboard = this.registries.dashboards.require(dashboardId);

    return this.resolveDashboard(dashboard);
  }

  /**
   * Resolve um Dashboard informado.
   */
  async resolveDashboard(dashboard: WorkspaceDashboard): Promise<WorkspaceResolvedDashboard> {
    const diagnostics: string[] = [];

    const layout = this.layoutEngine.resolveLayout(dashboard);

    if (dashboard.layoutId && !layout) {
      diagnostics.push(`Layout not found: ${dashboard.layoutId}`);
    }

    const regions = this.resolveRegions(layout, diagnostics);

    const state = await this.layoutEngine.loadState(dashboard.id);

    const widgets = this.resolveWidgets(dashboard.widgets, regions, diagnostics);

    const gridConfiguration = new WorkspaceGridConfigurationResolver().resolve(layout);

    const layoutCapabilities = new WorkspaceLayoutCapabilityResolver().resolve(layout);

    return {
      dashboard,
      layout,
      regions,
      widgets,
      state,
      gridConfiguration,
      layoutCapabilities,
      valid: diagnostics.length === 0,
      diagnostics,
    };
  }

  /**
   * Resolve as regiões pertencentes ao Layout.
   */
  private resolveRegions(
    layout: WorkspaceLayout | undefined,
    diagnostics: string[],
  ): readonly WorkspaceLayoutRegion[] {
    if (!layout) {
      return [];
    }

    const regions = this.layoutEngine.resolveRegions(layout);

    if (!layout.regionIds?.length) {
      return regions;
    }

    const resolvedRegionIds = new Set(regions.map((region) => region.id));

    for (const regionId of layout.regionIds) {
      if (!resolvedRegionIds.has(regionId)) {
        diagnostics.push(`Layout region not found or disabled: ${regionId}`);
      }
    }

    return regions;
  }

  /**
   * Resolve e valida as instâncias de Widgets.
   */
  private resolveWidgets(
    widgets: readonly WorkspaceWidgetInstance[] | undefined,
    regions: readonly WorkspaceLayoutRegion[],
    diagnostics: string[],
  ): readonly WorkspaceWidgetInstance[] {
    if (!widgets?.length) {
      return [];
    }

    const resolved: WorkspaceWidgetInstance[] = [];

    const resolvedRegionIds = new Set(regions.map((region) => region.id));

    for (const widget of widgets) {
      const definition = this.registries.widgets.get(widget.widgetId);

      if (!definition) {
        diagnostics.push(`Widget not registered: ${widget.widgetId}`);
        continue;
      }

      if (definition.enabled === false) {
        diagnostics.push(`Widget disabled: ${widget.widgetId}`);
        continue;
      }

      if (widget.regionId && !resolvedRegionIds.has(widget.regionId)) {
        diagnostics.push(`Widget region not found or disabled: ${widget.regionId}`);
      }

      resolved.push(widget);
    }

    return resolved;
  }
}
