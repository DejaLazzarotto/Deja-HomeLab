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
  Injectable,
} from '@angular/core';

import {
  WorkspaceResolvedDashboard,
} from '../../core/workspace-sdk/runtime/workspace-resolved-dashboard';

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
   * Renderiza um Workspace resolvido.
   *
   * Nesta primeira implementação o método estabelece apenas
   * a assinatura institucional. A criação dinâmica dos
   * componentes será implementada nas próximas etapas.
   */
  async render(
    dashboard: WorkspaceResolvedDashboard,
    host: AngularWorkspaceRenderHost,
  ): Promise<void> {

    void dashboard;
    void host;

  }

  /**
   * Libera todos os recursos utilizados pela renderização.
   */
  async dispose(): Promise<void> {

    // Implementação futura.

  }

}