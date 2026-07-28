/*
 * Deja Workspace UI SDK
 *
 * Workspace Incremental Render Operations
 *
 * Contratos institucionais responsáveis pela representação
 * das operações incrementais de renderização do Workspace.
 */

import {
  WorkspaceDashboardRegionId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceGridPosition,
  WorkspaceWidgetInstance,
} from './workspace-widget';

/**
 * Tipos institucionais de operações incrementais.
 */
export type WorkspaceIncrementalRenderOperationType =
  | 'move'
  | 'resize'
  | 'insert'
  | 'remove';

/**
 * Contrato base de uma operação incremental.
 */
export interface WorkspaceIncrementalRenderOperation {
  /**
   * Tipo institucional da operação.
   */
  readonly type: WorkspaceIncrementalRenderOperationType;
}

/**
 * Operação incremental de movimentação.
 */
export interface WorkspaceMoveRenderOperation
  extends WorkspaceIncrementalRenderOperation {

  readonly type: 'move';

  readonly widgetInstanceId: string;

  readonly regionId?: WorkspaceDashboardRegionId;

  readonly position: WorkspaceGridPosition;
}

/**
 * Operação incremental de redimensionamento.
 */
export interface WorkspaceResizeRenderOperation
  extends WorkspaceIncrementalRenderOperation {

  readonly type: 'resize';

  readonly widgetInstanceId: string;

  readonly columnSpan?: number;

  readonly rowSpan?: number;
}

/**
 * Operação incremental de inserção.
 */
export interface WorkspaceInsertRenderOperation
  extends WorkspaceIncrementalRenderOperation {

  readonly type: 'insert';

  readonly widget: WorkspaceWidgetInstance;
}

/**
 * Operação incremental de remoção.
 */
export interface WorkspaceRemoveRenderOperation
  extends WorkspaceIncrementalRenderOperation {

  readonly type: 'remove';

  readonly widgetInstanceId: string;
}

/**
 * União institucional das operações incrementais suportadas.
 */
export type WorkspaceIncrementalRenderOperationUnion =
  | WorkspaceMoveRenderOperation
  | WorkspaceResizeRenderOperation
  | WorkspaceInsertRenderOperation
  | WorkspaceRemoveRenderOperation;