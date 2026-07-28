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
  WorkspaceWidgetRenderAdapter,
} from './workspace-widget-render-adapter';

/**
 * Executor institucional das operações incrementais.
 *
 * Esta infraestrutura permanece completamente independente
 * da tecnologia concreta de renderização utilizada pelo
 * Workspace.
 *
 * O Executor interpreta a operação incremental e delega sua
 * execução ao WorkspaceWidgetRenderAdapter configurado pela
 * camada de integração.
 */
export class WorkspaceIncrementalRenderExecutor {

  constructor(
    private readonly adapter: WorkspaceWidgetRenderAdapter,
  ) {}

  /**
   * Executa uma operação incremental.
   *
   * Retorna true quando o Adapter executa a operação.
   *
   * Retorna false quando a operação não pode ser executada
   * incrementalmente, permitindo que a estratégia de
   * renderização utilize Full Render como fallback.
   */
  execute(
    operation: WorkspaceIncrementalRenderOperationUnion,
  ): boolean {

    switch (operation.type) {

      case 'move':

        return this.adapter.move(operation);

      case 'resize':

        return this.adapter.resize(operation);

      case 'insert':

        return this.adapter.insert(operation);

      case 'remove':

        return this.adapter.remove(operation);

    }

  }

}