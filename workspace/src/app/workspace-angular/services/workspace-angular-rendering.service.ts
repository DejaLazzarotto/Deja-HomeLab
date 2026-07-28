/*
 * Deja Workspace Angular Integration
 *
 * Workspace Angular Rendering Service
 *
 * Serviço responsável pela criação, gerenciamento e destruição
 * da árvore de componentes Angular utilizada pelo Workspace.
 *
 * Este serviço pertence exclusivamente à camada Angular,
 * preservando o Workspace SDK completamente independente
 * do framework.
 */

import {
  ComponentRef,
  Injectable,
} from '@angular/core';

import {
  WorkspaceDashboardStateUnsubscribe,
} from '../../core/workspace-sdk/runtime/workspace-dashboard-state';

import {
  WorkspaceResolvedDashboard,
} from '../../core/workspace-sdk/runtime/workspace-resolved-dashboard';

import {
  WorkspaceRuntime,
} from '../../core/workspace-sdk/runtime/workspace-runtime';

import {
  WorkspaceDashboardComponent,
} from '../components/workspace-dashboard/workspace-dashboard';

import {
  AngularWorkspaceRenderHost,
} from '../rendering/angular-workspace-render-host';

import {
  WorkspaceRenderStrategyFactory,
} from '../rendering/workspace-render-strategy-factory';

import {
  WorkspaceWidgetComponentCache,
} from '../rendering/workspace-widget-component-cache';

/**
 * Serviço oficial de renderização Angular.
 */
@Injectable({
  providedIn: 'root',
})
export class WorkspaceAngularRenderingService {

  /**
   * Referência do Dashboard Angular atualmente renderizado.
   */
  private dashboardComponentRef?:
    ComponentRef<WorkspaceDashboardComponent>;

  /**
   * Host atualmente associado ao componente renderizado.
   */
  private currentHost?: AngularWorkspaceRenderHost;

  /**
   * Runtime atualmente associado à renderização.
   */
  private currentRuntime?: WorkspaceRuntime;

  /**
   * Inscrição ativa no estado institucional do Dashboard.
   */
  private unsubscribeDashboardState?:
    WorkspaceDashboardStateUnsubscribe;

  /**
   * Factory institucional das estratégias de renderização.
   */
  private readonly renderStrategyFactory:
    WorkspaceRenderStrategyFactory;

  constructor(
    widgetComponentCache:
      WorkspaceWidgetComponentCache,
  ) {

    this.renderStrategyFactory =
      new WorkspaceRenderStrategyFactory(
        widgetComponentCache,
      );

  }

  /**
   * Renderiza um Workspace Dashboard resolvido.
   */
  async render(
    runtime: WorkspaceRuntime,
    dashboard: WorkspaceResolvedDashboard,
    host: AngularWorkspaceRenderHost,
  ): Promise<void> {

    const requiresComponentCreation =
      !this.dashboardComponentRef
      || this.currentHost !== host;

    const requiresStateSubscription =
      requiresComponentCreation
      || this.currentRuntime !== runtime;

    if (requiresComponentCreation) {

      await this.dispose();

      host.viewContainerRef.clear();

      this.dashboardComponentRef =
        host.viewContainerRef.createComponent(
          WorkspaceDashboardComponent,
          {
            environmentInjector:
              host.environmentInjector,
          },
        );

      this.currentHost = host;

    }

    if (!this.dashboardComponentRef) {

      throw new Error(
        'Workspace dashboard component could not be created.',
      );

    }

    const componentRef = this.dashboardComponentRef;

    componentRef.setInput(
      'runtime',
      runtime,
    );

    componentRef.setInput(
      'resolvedDashboard',
      dashboard,
    );

    if (requiresStateSubscription) {

      this.unsubscribeDashboardState?.();

      this.unsubscribeDashboardState = undefined;
      this.currentRuntime = runtime;

      if (runtime.dashboardState) {

        this.unsubscribeDashboardState =
          runtime.dashboardState.subscribe(
            (update) => {

              const strategy =
                this.renderStrategyFactory.create();

              strategy.render({
                runtime,
                update,
                dashboardComponent:
                  componentRef.instance,
              });

              componentRef.changeDetectorRef.markForCheck();

            },
          );

      }

    }

  }

  /**
   * Libera todos os recursos utilizados pela renderização.
   */
  async dispose(): Promise<void> {

    this.unsubscribeDashboardState?.();

    this.unsubscribeDashboardState = undefined;
    this.currentRuntime = undefined;

    if (!this.dashboardComponentRef) {

      this.currentHost = undefined;

      return;

    }

    this.dashboardComponentRef.destroy();

    this.dashboardComponentRef = undefined;
    this.currentHost = undefined;

  }

}