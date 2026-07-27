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
  private dashboardComponentRef?: ComponentRef<WorkspaceDashboardComponent>;

  /**
   * Host atualmente associado ao componente renderizado.
   */
  private currentHost?: AngularWorkspaceRenderHost;

  /**
   * Renderiza um Workspace Dashboard resolvido.
   */
  async render(
    runtime: WorkspaceRuntime,
    dashboard: WorkspaceResolvedDashboard,
    host: AngularWorkspaceRenderHost,
  ): Promise<void> {

    if (
      !this.dashboardComponentRef
      || this.currentHost !== host
    ) {

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

    const componentRef = this.dashboardComponentRef;

    componentRef.setInput(
      'runtime',
      runtime,
    );

    componentRef.setInput(
      'resolvedDashboard',
      dashboard,
    );

    if (runtime.dashboardState) {

      componentRef.setInput(
        'dashboardState',
        runtime.dashboardState,
      );

    }

  }

  /**
   * Libera todos os recursos utilizados pela renderização.
   */
  async dispose(): Promise<void> {

    if (!this.dashboardComponentRef) {
      return;
    }

    this.dashboardComponentRef.destroy();

    this.dashboardComponentRef = undefined;
    this.currentHost = undefined;

  }

}