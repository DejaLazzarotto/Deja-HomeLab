/*
 * Deja Workspace UI
 *
 * Workspace Render Strategy
 *
 * Contrato institucional das estratégias responsáveis pela
 * aplicação de atualizações de Dashboard.
 */

import {
  WorkspaceRenderContext,
} from './workspace-render-context';

/**
 * Contrato institucional implementado por todas as
 * estratégias de renderização do Workspace.
 *
 * As estratégias permanecem responsáveis exclusivamente
 * pela aplicação das atualizações recebidas do
 * WorkspaceDashboardState, mantendo o WorkspaceDashboardComponent
 * completamente desacoplado das regras de atualização.
 */
export interface WorkspaceRenderStrategy {

  /**
   * Aplica uma atualização de Dashboard utilizando a
   * estratégia de renderização correspondente.
   */
  render(
    context: WorkspaceRenderContext,
  ): void;

}