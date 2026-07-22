import {
  WorkspaceRuntimeContext,
} from '../models/workspace-models';
import {
  WorkspaceRuntimeExtensionContext,
  WorkspaceRuntimeExtensionPointId,
} from './workspace-runtime-extension-point';
import {
  WorkspaceRuntimeExtensionRegistry,
} from './workspace-runtime-extension-registry';

/**
 * Resultado individual produzido por uma extensão executada.
 */
export interface WorkspaceRuntimeExtensionDispatchResult<TResult = unknown> {
  /**
   * Identificador da extensão executada.
   */
  readonly extensionId: string;

  /**
   * Resultado retornado pelo handler.
   */
  readonly result: TResult;
}

/**
 * Erro lançado quando a execução de uma extensão falha.
 */
export class WorkspaceRuntimeExtensionDispatchError extends Error {
  override readonly cause: unknown;

  constructor(
    readonly extensionId: string,
    readonly extensionPoint: WorkspaceRuntimeExtensionPointId,
    cause: unknown,
  ) {
    super(
      `Workspace runtime extension dispatch failed: ${extensionId} at ${extensionPoint}`,
      { cause },
    );

    this.name = 'WorkspaceRuntimeExtensionDispatchError';
    this.cause = cause;
  }
}

/**
 * Dispatcher oficial das extensões do Workspace Runtime.
 *
 * Responsabilidades:
 * - localizar extensões habilitadas por ponto de extensão;
 * - preservar a ordenação definida pelo registry;
 * - construir o contexto de execução;
 * - executar handlers síncronos e assíncronos;
 * - interromper o fluxo quando uma extensão falhar;
 * - preservar independência de Angular.
 */
export class WorkspaceRuntimeExtensionDispatcher {
  constructor(
    private readonly registry: WorkspaceRuntimeExtensionRegistry,
  ) {}

  /**
   * Executa todas as extensões habilitadas de um ponto de extensão.
   *
   * As extensões são executadas sequencialmente, respeitando a prioridade
   * estabelecida pelo WorkspaceRuntimeExtensionRegistry.
   *
   * @throws WorkspaceRuntimeExtensionDispatchError
   * quando um handler falhar.
   */
  async dispatch<TPayload = unknown, TResult = unknown>(
    extensionPoint: WorkspaceRuntimeExtensionPointId,
    payload: TPayload,
    runtimeContext?: WorkspaceRuntimeContext,
  ): Promise<readonly WorkspaceRuntimeExtensionDispatchResult<TResult>[]> {
    const extensions =
      this.registry.listByExtensionPoint(extensionPoint);

    const results: WorkspaceRuntimeExtensionDispatchResult<TResult>[] = [];

    for (const extension of extensions) {
      const context: WorkspaceRuntimeExtensionContext<TPayload> = {
        extensionPoint,
        runtimeContext,
        payload,
      };

      try {
        const result = await extension.handler(context);

        results.push({
          extensionId: extension.id,
          result: result as TResult,
        });
      } catch (error) {
        throw new WorkspaceRuntimeExtensionDispatchError(
          extension.id,
          extensionPoint,
          error,
        );
      }
    }

    return Object.freeze(results);
  }

  /**
   * Executa todas as extensões e retorna somente seus resultados.
   */
  async dispatchResults<TPayload = unknown, TResult = unknown>(
    extensionPoint: WorkspaceRuntimeExtensionPointId,
    payload: TPayload,
    runtimeContext?: WorkspaceRuntimeContext,
  ): Promise<readonly TResult[]> {
    const dispatchResults = await this.dispatch<TPayload, TResult>(
      extensionPoint,
      payload,
      runtimeContext,
    );

    return Object.freeze(
      dispatchResults.map((dispatchResult) => dispatchResult.result),
    );
  }

  /**
   * Informa se existem extensões habilitadas para um ponto de extensão.
   */
  hasHandlers(
    extensionPoint: WorkspaceRuntimeExtensionPointId,
  ): boolean {
    return this.registry.count(extensionPoint) > 0;
  }
}