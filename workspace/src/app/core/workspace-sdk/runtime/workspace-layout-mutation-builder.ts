/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Mutation Builder
 *
 * Responsável pela construção institucional das mutações
 * estruturais do Workspace Layout.
 */

import {
  WorkspaceDashboardRegionId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceGridPosition,
  WorkspaceWidgetInstance,
} from './workspace-widget';

import {
  WorkspaceInsertWidgetMutation,
  WorkspaceLayoutMutationOperation,
  WorkspaceMoveWidgetMutation,
  WorkspaceResizeWidgetMutation,
} from './workspace-layout-mutation';

/**
 * Factory institucional das mutações de Layout.
 *
 * Esta infraestrutura permanece independente:
 *
 * - da Workspace Editing API;
 * - do Workspace Layout Controller;
 * - da Workspace Layout Session;
 * - do mecanismo de persistência;
 * - da tecnologia de renderização.
 *
 * Toda mutação estrutural deverá ser construída
 * exclusivamente através desta infraestrutura.
 */
export class WorkspaceLayoutMutationBuilder {

  /**
   * Constrói uma mutação institucional.
   *
   * Mantido para compatibilidade durante a transição
   * para a API de operações de alto nível.
   */
  build(
    mutation: WorkspaceLayoutMutationOperation,
  ): WorkspaceLayoutMutationOperation {

    return mutation;

  }

  /**
   * Constrói uma mutação de movimentação de Widget.
   */
  moveWidget(
    widgetInstanceId: string,
    position: WorkspaceGridPosition,
    regionId?: WorkspaceDashboardRegionId,
  ): WorkspaceMoveWidgetMutation {

    return {
      type: 'move-widget',
      widgetInstanceId,
      regionId,
      position,
    };

  }

  /**
   * Constrói uma mutação de redimensionamento de Widget.
   */
  resizeWidget(
    widgetInstanceId: string,
    columnSpan?: number,
    rowSpan?: number,
  ): WorkspaceResizeWidgetMutation {

    return {
      type: 'resize-widget',
      widgetInstanceId,
      columnSpan,
      rowSpan,
    };

  }

  /**
   * Constrói uma mutação de inclusão de Widget.
   */
  addWidget(
    widget: WorkspaceWidgetInstance,
  ): WorkspaceInsertWidgetMutation {

    return {
      type: 'insert-widget',
      widget,
    };

  }

  /**
   * Cria uma mutação para remoção de Widget.
   *
   * Mantido temporariamente durante a evolução
   * da Workspace Editing API.
   */
  removeWidget(
    mutation: WorkspaceLayoutMutationOperation,
  ): WorkspaceLayoutMutationOperation {

    return this.build(mutation);

  }

}