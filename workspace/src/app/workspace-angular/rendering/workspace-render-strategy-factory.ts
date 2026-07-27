/*
 * Deja Workspace UI
 *
 * Workspace Render Strategy Factory
 *
 * Factory institucional responsável pela resolução da
 * estratégia de renderização do Workspace.
 */

import {
  WorkspaceFullRenderStrategy,
} from './workspace-full-render-strategy';

import {
  WorkspaceIncrementalRenderStrategy,
} from './workspace-incremental-render-strategy';

import {
  WorkspaceRenderStrategy,
} from './workspace-render-strategy';

/**
 * Factory responsável pela composição e resolução das
 * estratégias de renderização do Workspace.
 *
 * Nesta etapa, toda atualização é direcionada para a
 * estratégia incremental, que ainda utiliza internamente
 * a renderização completa como mecanismo de fallback.
 */
export class WorkspaceRenderStrategyFactory {

  private readonly fullRenderStrategy =
    new WorkspaceFullRenderStrategy();

  private readonly incrementalRenderStrategy =
    new WorkspaceIncrementalRenderStrategy(
      this.fullRenderStrategy,
    );

  /**
   * Resolve a estratégia institucional de renderização.
   */
  create(): WorkspaceRenderStrategy {

    return this.incrementalRenderStrategy;

  }

}