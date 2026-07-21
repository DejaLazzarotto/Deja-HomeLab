import {
  WorkspaceOwnerId,
  WorkspacePriority,
  WorkspaceResourceId,
} from '../contracts/workspace-contracts';
import {
  WorkspaceRuntimeContext,
} from '../models/workspace-models';

/**
 * Identificador público de um ponto de extensão do Workspace Runtime.
 *
 * Exemplos:
 * - workspace.navigation.items
 * - workspace.toolbar.actions
 * - workspace.dashboard.widgets
 */
export type WorkspaceRuntimeExtensionPointId = WorkspaceResourceId;

/**
 * Identificador único de uma extensão registrada.
 *
 * O identificador pertence à extensão concreta, enquanto
 * extensionPoint identifica o ponto no qual ela será executada.
 */
export type WorkspaceRuntimeExtensionId = WorkspaceResourceId;

/**
 * Contexto fornecido durante a execução de uma extensão.
 */
export interface WorkspaceRuntimeExtensionContext<TPayload = unknown> {
  /**
   * Ponto de extensão atualmente executado.
   */
  readonly extensionPoint: WorkspaceRuntimeExtensionPointId;

  /**
   * Contexto institucional do Workspace Runtime.
   */
  readonly runtimeContext?: WorkspaceRuntimeContext;

  /**
   * Dados fornecidos pelo chamador do ponto de extensão.
   */
  readonly payload: TPayload;
}

/**
 * Handler executável de uma extensão do Workspace Runtime.
 */
export type WorkspaceRuntimeExtensionHandler<
  TPayload = unknown,
  TResult = unknown,
> = (
  context: WorkspaceRuntimeExtensionContext<TPayload>,
) => TResult | Promise<TResult>;

/**
 * Extensão concreta registrada em um ponto de extensão.
 */
export interface WorkspaceRuntimeExtension<
  TPayload = unknown,
  TResult = unknown,
> {
  /**
   * Identificador público e único da extensão.
   */
  readonly id: WorkspaceRuntimeExtensionId;

  /**
   * Ponto de extensão ao qual esta implementação pertence.
   */
  readonly extensionPoint: WorkspaceRuntimeExtensionPointId;

  /**
   * Módulo, domínio ou extensão proprietária do registro.
   */
  readonly owner: WorkspaceOwnerId;

  /**
   * Prioridade de execução.
   *
   * Valores menores são executados primeiro.
   */
  readonly priority?: WorkspacePriority;

  /**
   * Indica se a extensão está habilitada.
   *
   * Quando omitido, o registro é considerado habilitado.
   */
  readonly enabled?: boolean;

  /**
   * Handler executado pelo dispatcher.
   */
  readonly handler: WorkspaceRuntimeExtensionHandler<TPayload, TResult>;
}
