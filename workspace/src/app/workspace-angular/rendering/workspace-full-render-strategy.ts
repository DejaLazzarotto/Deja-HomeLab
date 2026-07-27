/*
 * Deja Workspace UI
 *
 * Workspace Full Render Strategy
 *
 * Estratégia institucional responsável pela aplicação
 * completa de uma atualização de Dashboard.
 */

import {
  WorkspaceRenderContext,
} from './workspace-render-context';

import {
  WorkspaceRenderStrategy,
} from './workspace-render-strategy';

/**
 * Estratégia responsável pela renderização completa do
 * Dashboard.
 *
 * Nesta etapa, a estratégia preserva o comportamento atual,
 * substituindo integralmente o Dashboard resolvido apresentado
 * pelo componente.
 */
export class WorkspaceFullRenderStrategy
  implements WorkspaceRenderStrategy {

  /**
   * Aplica uma atualização completa do Dashboard.
   */
  render(
    context: WorkspaceRenderContext,
  ): void {

    context.dashboardComponent.resolvedDashboard =
      context.update.dashboard;

  }

}