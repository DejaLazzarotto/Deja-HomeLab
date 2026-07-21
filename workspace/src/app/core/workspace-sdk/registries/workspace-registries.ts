import {
  WorkspaceDashboardId,
  WorkspaceDomainId,
  WorkspaceNavigationId,
  WorkspaceServiceId,
  WorkspaceViewId,
  WorkspaceWidgetId,
} from '../contracts/workspace-contracts';
import {
  WorkspaceDashboard,
  WorkspaceDomain,
  WorkspaceNavigationItem,
  WorkspaceServiceDefinition,
  WorkspaceView,
  WorkspaceWidget,
} from '../models/workspace-models';
import { WorkspaceRegistry } from './workspace-registry';

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
  listByDomain(domainId: WorkspaceDomainId): readonly WorkspaceView[] {
    return this.list().filter((view) => view.domainId === domainId);
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
    return this.list().filter((item) => !item.parentId);
  }

  listChildren(
    parentId: WorkspaceNavigationId,
  ): readonly WorkspaceNavigationItem[] {
    return this.list().filter((item) => item.parentId === parentId);
  }

  listVisible(): readonly WorkspaceNavigationItem[] {
    return this.list({ enabled: true }).filter(
      (item) => item.visible !== false,
    );
  }
}

/**
 * Registry oficial de widgets do Workspace.
 */
export class WorkspaceWidgetRegistry extends WorkspaceRegistry<
  WorkspaceWidget,
  WorkspaceWidgetId
> {
  listByType(widgetType: string): readonly WorkspaceWidget[] {
    return this.list().filter((widget) => widget.widgetType === widgetType);
  }
}

/**
 * Registry oficial de dashboards do Workspace.
 */
export class WorkspaceDashboardRegistry extends WorkspaceRegistry<
  WorkspaceDashboard,
  WorkspaceDashboardId
> {}

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
 * Mantém uma única composição compartilhável pelo runtime,
 * serviços públicos e testes.
 */
export class WorkspaceRegistries {
  readonly domains = new WorkspaceDomainRegistry();
  readonly views = new WorkspaceViewRegistry();
  readonly navigation = new WorkspaceNavigationRegistry();
  readonly widgets = new WorkspaceWidgetRegistry();
  readonly dashboards = new WorkspaceDashboardRegistry();
  readonly services = new WorkspaceServiceRegistry();

  clear(): void {
    this.domains.clear();
    this.views.clear();
    this.navigation.clear();
    this.widgets.clear();
    this.dashboards.clear();
    this.services.clear();
  }
}
