/*
 * Deja Workspace UI
 *
 * Workspace Incremental Render Strategy
 *
 * Estratégia institucional responsável pela aplicação
 * incremental de atualizações do Dashboard.
 */

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
 * Estratégia institucional preparada para a futura
 * renderização incremental do Workspace.
 *
 * Nesta etapa (W17.5), toda atualização permanece utilizando
 * a estratégia de renderização completa como mecanismo de
 * fallback, preservando integralmente o comportamento atual.
 *
 * Nas etapas seguintes esta infraestrutura passará a atualizar
 * apenas os Widgets efetivamente afetados por cada mutação.
 */
export class WorkspaceIncrementalRenderStrategy
  implements WorkspaceRenderStrategy {

  constructor(
    private readonly fullRenderStrategy =
      new WorkspaceFullRenderStrategy(),
  ) {}

  /**
   * Aplica uma atualização incremental.
   *
   * Enquanto a infraestrutura incremental não estiver
   * implementada, a atualização é delegada para a estratégia
   * de renderização completa.
   */
  render(
    context: WorkspaceRenderContext,
  ): void {

    this.fullRenderStrategy.render(
      context,
    );

  }

}