/*
 * Deja Workspace UI
 *
 * Workspace Incremental Render Strategy
 *
 * Estratégia institucional responsável pela aplicação
 * incremental de atualizações do Dashboard.
 */

import {
  WorkspaceIncrementalRenderExecutor,
} from '../../core/workspace-sdk/runtime/workspace-incremental-render-executor';

import {
  WorkspaceIncrementalRenderOperationFactory,
} from '../../core/workspace-sdk/runtime/workspace-incremental-render-operation-factory';

import {
  WorkspaceRenderContext,
} from './workspace-render-context';

import {
  WorkspaceFullRenderStrategy,
} from './workspace-full-render-strategy';

import {
  WorkspaceRenderStrategy,
} from './workspace-render-strategy';

/**
 * Estratégia institucional responsável por interpretar
 * mutações de Layout e tentar aplicá-las incrementalmente.
 *
 * Quando a mutação não puder ser processada pelo mecanismo
 * incremental, a estratégia utiliza a renderização completa
 * como fallback.
 */
export class WorkspaceIncrementalRenderStrategy
  implements WorkspaceRenderStrategy {

  constructor(
    private readonly operationFactory:
      WorkspaceIncrementalRenderOperationFactory,

    private readonly executor:
      WorkspaceIncrementalRenderExecutor,

    private readonly fullRenderStrategy:
      WorkspaceFullRenderStrategy,
  ) {}

  /**
   * Aplica uma atualização do Dashboard.
   */
  render(
    context: WorkspaceRenderContext,
  ): void {

    const mutation =
      context.update.mutation;

    if (!mutation) {

      this.fullRenderStrategy.render(
        context,
      );

      return;

    }

    const operation =
      this.operationFactory.create(
        mutation,
      );

    const executed =
      this.executor.execute(
        operation,
      );

    if (executed) {

      return;

    }

    this.fullRenderStrategy.render(
      context,
    );

  }

}