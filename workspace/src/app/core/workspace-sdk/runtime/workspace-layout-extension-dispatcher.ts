/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Extension Dispatcher
 *
 * Infraestrutura institucional responsável pela resolução
 * e execução ordenada das Workspace Layout Extensions.
 */

import {
  WorkspaceLayoutExtensionContext,
  WorkspaceLayoutExtensionPointId,
} from './workspace-layout-extension-point';

import {
  WorkspaceLayoutExtensionRegistry,
} from './workspace-layout-extension-registry';

/**
 * Resultado individual produzido pela execução
 * de uma Workspace Layout Extension.
 */
export interface WorkspaceLayoutExtensionResult<TResult = unknown> {

  /**
   * Identificador da extensão executada.
   */
  readonly extensionId: string;

  /**
   * Resultado retornado pelo handler da extensão.
   */
  readonly result: TResult;

}

/**
 * Responsável pela execução institucional das extensões
 * registradas para os pontos de extensão do Workspace Layout.
 *
 * As extensões são executadas sequencialmente, respeitando
 * a ordem resolvida pelo WorkspaceLayoutExtensionRegistry.
 */
export class WorkspaceLayoutExtensionDispatcher {

  constructor(
    private readonly registry: WorkspaceLayoutExtensionRegistry,
  ) {}

  /**
   * Executa todas as extensões habilitadas associadas
   * ao ponto de extensão informado.
   *
   * A execução ocorre sequencialmente para preservar
   * previsibilidade, prioridade e ordem institucional.
   */
  async dispatch<
    TPayload = unknown,
    TResult = unknown,
  >(
    extensionPoint: WorkspaceLayoutExtensionPointId,
    payload: TPayload,
  ): Promise<readonly WorkspaceLayoutExtensionResult<TResult>[]> {

    const extensions = this.registry.listByExtensionPoint(
      extensionPoint,
    );

    const results: WorkspaceLayoutExtensionResult<TResult>[] = [];

    for (const extension of extensions) {

      const context: WorkspaceLayoutExtensionContext<TPayload> = {
        extensionPoint,
        payload,
      };

      const result = await extension.handler(
        context,
      ) as TResult;

      results.push({
        extensionId: extension.id,
        result,
      });

    }

    return results;

  }

}