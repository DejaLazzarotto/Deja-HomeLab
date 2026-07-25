/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Mutation Contracts
 *
 * Contratos institucionais responsáveis pela definição das
 * mutações estruturadas aplicáveis aos Layouts do Workspace.
 */

import {
  WorkspaceDashboardRegionId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceResolvedDashboard,
} from './workspace-resolved-dashboard';

import {
  WorkspaceGridPosition,
  WorkspaceWidgetInstance,
} from './workspace-widget';

/**
 * Tipos institucionais de mutação suportados pelo Workspace Layout.
 */
export type WorkspaceLayoutMutationType =
  | 'move-widget'
  | 'resize-widget'
  | 'insert-widget'
  | 'remove-widget';

/**
 * Contrato base de uma mutação institucional do Workspace Layout.
 *
 * Toda mutação representa uma intenção declarativa de alteração,
 * permanecendo independente de mecanismos visuais, eventos de
 * interface, bibliotecas de Drag-and-Drop ou infraestrutura Angular.
 */
export interface WorkspaceLayoutMutation {
  /**
   * Tipo institucional da mutação.
   */
  readonly type: WorkspaceLayoutMutationType;
}

/**
 * Mutação responsável pela movimentação de uma instância de Widget.
 */
export interface WorkspaceMoveWidgetMutation
  extends WorkspaceLayoutMutation {

  /**
   * Tipo discriminador da mutação.
   */
  readonly type: 'move-widget';

  /**
   * Identificador da instância que será movimentada.
   */
  readonly widgetInstanceId: string;

  /**
   * Nova região do Layout.
   *
   * Quando omitida, a região atual será preservada.
   */
  readonly regionId?: WorkspaceDashboardRegionId;

  /**
   * Nova posição declarativa da instância.
   */
  readonly position: WorkspaceGridPosition;
}

/**
 * Mutação responsável pelo redimensionamento de uma instância de Widget.
 */
export interface WorkspaceResizeWidgetMutation
  extends WorkspaceLayoutMutation {

  /**
   * Tipo discriminador da mutação.
   */
  readonly type: 'resize-widget';

  /**
   * Identificador da instância que será redimensionada.
   */
  readonly widgetInstanceId: string;

  /**
   * Quantidade de colunas ocupadas após o redimensionamento.
   */
  readonly columnSpan?: number;

  /**
   * Quantidade de linhas ocupadas após o redimensionamento.
   */
  readonly rowSpan?: number;
}

/**
 * Mutação responsável pela inserção de uma instância de Widget.
 */
export interface WorkspaceInsertWidgetMutation
  extends WorkspaceLayoutMutation {

  /**
   * Tipo discriminador da mutação.
   */
  readonly type: 'insert-widget';

  /**
   * Instância que será inserida no Dashboard.
   */
  readonly widget: WorkspaceWidgetInstance;
}

/**
 * Mutação responsável pela remoção de uma instância de Widget.
 */
export interface WorkspaceRemoveWidgetMutation
  extends WorkspaceLayoutMutation {

  /**
   * Tipo discriminador da mutação.
   */
  readonly type: 'remove-widget';

  /**
   * Identificador da instância que será removida.
   */
  readonly widgetInstanceId: string;
}

/**
 * União institucional das mutações concretas suportadas.
 */
export type WorkspaceLayoutMutationOperation =
  | WorkspaceMoveWidgetMutation
  | WorkspaceResizeWidgetMutation
  | WorkspaceInsertWidgetMutation
  | WorkspaceRemoveWidgetMutation;

/**
 * Resultado institucional da aplicação de uma mutação.
 */
export interface WorkspaceLayoutMutationResult {
  /**
   * Mutação processada.
   */
  readonly mutation: WorkspaceLayoutMutationOperation;

  /**
   * Indica se a mutação foi aplicada com sucesso.
   */
  readonly applied: boolean;

  /**
   * Dashboard resultante.
   *
   * Quando a mutação não puder ser aplicada, contém o mesmo
   * Dashboard resolvido recebido pela infraestrutura de mutação.
   */
  readonly dashboard: WorkspaceResolvedDashboard;

  /**
   * Diagnósticos produzidos durante o processamento.
   */
  readonly diagnostics: readonly string[];
}