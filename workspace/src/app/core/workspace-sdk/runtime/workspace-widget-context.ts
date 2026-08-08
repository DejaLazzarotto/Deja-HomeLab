/*
 * Deja Workspace UI SDK
 *
 * Workspace Widget Context
 *
 * Contrato institucional responsável por fornecer aos
 * componentes visuais um contexto controlado de execução.
 *
 * Este contrato permanece independente do Workspace Runtime,
 * de Dispatchers e de tecnologias concretas de interface.
 */

import {
  WorkspaceActionId,
  WorkspaceActionResult,
} from './workspace-action';

import {
  WorkspaceWidget,
  WorkspaceWidgetInstance,
} from './workspace-widget';

/**
 * Contexto institucional disponibilizado a um componente
 * visual de Workspace Widget.
 *
 * Permite consultar e executar Actions sem expor diretamente
 * o Workspace Runtime ou seus Dispatchers internos.
 */
export interface WorkspaceWidgetContext {

  /**
   * Definição institucional do Widget renderizado.
   */
  readonly widget: WorkspaceWidget;

  /**
   * Instância do Widget pertencente ao Dashboard.
   */
  readonly widgetInstance: WorkspaceWidgetInstance;

  /**
   * Verifica se uma Action pode ser executada pelo Widget.
   */
  canExecuteAction<TPayload = unknown>(
    actionId: WorkspaceActionId,
    payload?: TPayload,
    metadata?: Readonly<Record<string, unknown>>,
  ): Promise<boolean>;

  /**
   * Executa uma Action com origem institucional no Widget.
   */
  dispatchAction<
    TPayload = unknown,
    TResult = unknown,
  >(
    actionId: WorkspaceActionId,
    payload?: TPayload,
    metadata?: Readonly<Record<string, unknown>>,
  ): Promise<WorkspaceActionResult<TResult>>;

}