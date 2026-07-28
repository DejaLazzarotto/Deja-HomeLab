/*
 * Deja Workspace UI SDK
 *
 * Workspace Incremental Render Executor
 *
 * Infraestrutura institucional responsável pela execução
 * das operações incrementais de renderização.
 */

import {
  WorkspaceIncrementalRenderOperationUnion,
} from './workspace-incremental-render-operation';

import {
  WorkspaceWidgetReferenceRegistry,
} from './workspace-widget-reference-registry';

/**
 * Executor institucional das operações incrementais.
 *
 * Esta infraestrutura permanece completamente independente
 * da tecnologia de renderização utilizada pelo Workspace.
 *
 * Nesta primeira implementação o Executor apenas resolve
 * a referência institucional do Widget afetado, preparando
 * a evolução futura para atualização incremental do renderer.
 */
export class WorkspaceIncrementalRenderExecutor {

  constructor(
    private readonly registry: WorkspaceWidgetReferenceRegistry,
  ) {}

  /**
   * Executa uma operação incremental.
   *
   * Retorna true quando a infraestrutura conseguiu localizar
   * o Widget alvo da operação.
   */
  execute(
    operation: WorkspaceIncrementalRenderOperationUnion,
  ): boolean {

    switch (operation.type) {

      case 'insert':

        /*
         * Inserções continuam utilizando Full Render
         * nesta primeira versão.
         */
        return false;

      case 'move':

        return this.registry.get(
          operation.widgetInstanceId,
        ) !== undefined;

      case 'resize':

        return this.registry.get(
          operation.widgetInstanceId,
        ) !== undefined;

      case 'remove':

        return this.registry.get(
          operation.widgetInstanceId,
        ) !== undefined;

    }

  }

}