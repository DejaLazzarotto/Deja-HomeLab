import {
  WorkspaceDashboardId,
  WorkspaceDashboardLayoutId,
  WorkspaceDashboardRegionId,
  WorkspaceDomainId,
  WorkspaceNavigationId,
  WorkspaceServiceId,
  WorkspaceViewId,
  WorkspaceWidgetCapability,
  WorkspaceWidgetCategory,
  WorkspaceWidgetId,
  WorkspaceWidgetSurface,
} from '../contracts/workspace-contracts';

import {
  WorkspaceDashboard,
  WorkspaceDomain,
  WorkspaceNavigationItem,
  WorkspaceServiceDefinition,
  WorkspaceView,
  WorkspaceWidget,
} from '../models/workspace-models';

import {
  WorkspaceActionId,
} from '../runtime/workspace-action';

import {
  WorkspaceLayout,
} from '../runtime/workspace-layout';

import {
  WorkspaceLayoutRegion,
} from '../runtime/workspace-layout-region';

import {
  WorkspaceRegistry,
} from './workspace-registry';

/**
 * Registry oficial de domínios do Workspace.
 */
export class WorkspaceDomainRegistry extends WorkspaceRegistry<
  WorkspaceDomain,
  WorkspaceDomainId
> {}

/**
 * Registry oficial de views do Workspace.
 */
export class WorkspaceViewRegistry extends WorkspaceRegistry<
  WorkspaceView,
  WorkspaceViewId
> {

  listByDomain(
    domainId: WorkspaceDomainId,
  ): readonly WorkspaceView[] {
    return this.list().filter(
      (view) => view.domainId === domainId,
    );
  }

}

/**
 * Registry oficial de navegação do Workspace.
 */
export class WorkspaceNavigationRegistry extends WorkspaceRegistry<
  WorkspaceNavigationItem,
  WorkspaceNavigationId
> {

  listRootItems(): readonly WorkspaceNavigationItem[] {
    return this.list().filter(
      (item) => !item.parentId,
    );
  }

  listChildren(
    parentId: WorkspaceNavigationId,
  ): readonly WorkspaceNavigationItem[] {
    return this.list().filter(
      (item) => item.parentId === parentId,
    );
  }

  listVisible(): readonly WorkspaceNavigationItem[] {
    return this.list({
      enabled: true,
    }).filter(
      (item) => item.visible !== false,
    );
  }

}

/**
 * Registry oficial de Widgets do Workspace.
 */
export class WorkspaceWidgetRegistry extends WorkspaceRegistry<
  WorkspaceWidget,
  WorkspaceWidgetId
> {

  /**
   * Retorna Widgets de um determinado tipo.
   */
  listByType(
    widgetType: string,
  ): readonly WorkspaceWidget[] {
    return this.list().filter(
      (widget) => widget.widgetType === widgetType,
    );
  }

  /**
   * Retorna Widgets pertencentes a uma categoria.
   */
  listByCategory(
    category: WorkspaceWidgetCategory,
  ): readonly WorkspaceWidget[] {
    return this.list().filter(
      (widget) => widget.category === category,
    );
  }

  /**
   * Retorna Widgets compatíveis com uma superfície.
   */
  listBySurface(
    surface: WorkspaceWidgetSurface,
  ): readonly WorkspaceWidget[] {
    return this.list().filter(
      (widget) =>
        widget.supportedSurfaces?.includes(surface) ?? false,
    );
  }

  /**
   * Retorna Widgets que implementam determinada capacidade.
   */
  listByCapability(
    capability: WorkspaceWidgetCapability,
  ): readonly WorkspaceWidget[] {
    return this.list().filter(
      (widget) =>
        widget.capabilities?.includes(capability) ?? false,
    );
  }

  /**
   * Retorna Widgets cuja Action principal corresponde
   * ao identificador informado.
   */
  listByPrimaryAction(
    actionId: WorkspaceActionId,
  ): readonly WorkspaceWidget[] {
    return this.list().filter(
      (widget) => widget.primaryActionId === actionId,
    );
  }

  /**
   * Retorna Widgets que utilizam determinada Action.
   *
   * A consulta considera tanto a Action principal quanto
   * as Actions auxiliares declaradas pelo Widget.
   */
  listByAction(
    actionId: WorkspaceActionId,
  ): readonly WorkspaceWidget[] {
    return this.list().filter(
      (widget) =>
        widget.primaryActionId === actionId ||
        (widget.actionIds?.includes(actionId) ?? false),
    );
  }

  /**
   * Verifica se alguma Action declarada pelo Widget
   * corresponde ao identificador informado.
   */
  usesAction(
    widgetId: WorkspaceWidgetId,
    actionId: WorkspaceActionId,
  ): boolean {
    const widget = this.get(widgetId);

    if (!widget) {
      return false;
    }

    return (
      widget.primaryActionId === actionId ||
      (widget.actionIds?.includes(actionId) ?? false)
    );
  }

  /**
   * Retorna Widgets configuráveis.
   */
  listConfigurable(): readonly WorkspaceWidget[] {
    return this.listByCapability('configurable');
  }

  /**
   * Retorna Widgets interativos.
   */
  listInteractive(): readonly WorkspaceWidget[] {
    return this.listByCapability('interactive');
  }

  /**
   * Retorna Widgets atualizáveis.
   */
  listRefreshable(): readonly WorkspaceWidget[] {
    return this.listByCapability('refreshable');
  }

}

/**
 * Registry oficial de Dashboards do Workspace.
 */
export class WorkspaceDashboardRegistry extends WorkspaceRegistry<
  WorkspaceDashboard,
  WorkspaceDashboardId
> {}

/**
 * Registry oficial de Layouts do Workspace.
 */
export class WorkspaceLayoutRegistry extends WorkspaceRegistry<
  WorkspaceLayout,
  WorkspaceDashboardLayoutId
> {}

/**
 * Registry oficial de regiões de Layout do Workspace.
 */
export class WorkspaceLayoutRegionRegistry extends WorkspaceRegistry<
  WorkspaceLayoutRegion,
  WorkspaceDashboardRegionId
> {

  /**
   * Retorna regiões pertencentes ao conjunto informado.
   *
   * A ordenação institucional definida pelo WorkspaceRegistry
   * é preservada.
   */
  listByIds(
    regionIds: readonly WorkspaceDashboardRegionId[],
  ): readonly WorkspaceLayoutRegion[] {
    const allowedRegionIds = new Set(regionIds);

    return this.list().filter(
      (region) => allowedRegionIds.has(region.id),
    );
  }

}

/**
 * Registry oficial de serviços do Workspace.
 */
export class WorkspaceServiceRegistry extends WorkspaceRegistry<
  WorkspaceServiceDefinition,
  WorkspaceServiceId
> {}

/**
 * Agregador institucional dos registries do Workspace SDK.
 *
 * Mantém uma única composição compartilhável pelo Runtime,
 * serviços públicos e testes.
 */
export class WorkspaceRegistries {

  readonly domains = new WorkspaceDomainRegistry();

  readonly views = new WorkspaceViewRegistry();

  readonly navigation = new WorkspaceNavigationRegistry();

  readonly widgets = new WorkspaceWidgetRegistry();

  readonly dashboards = new WorkspaceDashboardRegistry();

  readonly layouts = new WorkspaceLayoutRegistry();

  readonly layoutRegions = new WorkspaceLayoutRegionRegistry();

  readonly services = new WorkspaceServiceRegistry();

  clear(): void {
    this.domains.clear();
    this.views.clear();
    this.navigation.clear();
    this.widgets.clear();
    this.dashboards.clear();
    this.layouts.clear();
    this.layoutRegions.clear();
    this.services.clear();
  }

}
