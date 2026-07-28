/*
 * Deja Workspace UI SDK
 *
 * Workspace Incremental Render Operation Factory
 *
 * Infraestrutura institucional responsável pela conversão
 * de mutações de Layout em operações incrementais de renderização.
 */

import {
  WorkspaceLayoutMutationOperation,
} from './workspace-layout-mutation';

import {
  WorkspaceIncrementalRenderOperationUnion,
} from './workspace-incremental-render-operation';

/**
 * Factory responsável pela interpretação institucional das
 * mutações de Layout do Workspace.
 *
 * A infraestrutura permanece independente:
 *
 * - do Angular;
 * - da tecnologia de renderização;
 * - do cache de componentes;
 * - da infraestrutura visual de Grid.
 */
export class WorkspaceIncrementalRenderOperationFactory {

  /**
   * Converte uma mutação de Layout em uma operação incremental.
   */
  create(
    mutation: WorkspaceLayoutMutationOperation,
  ): WorkspaceIncrementalRenderOperationUnion {

    switch (mutation.type) {

      case 'move-widget':

        return {
          type: 'move',
          widgetInstanceId: mutation.widgetInstanceId,
          regionId: mutation.regionId,
          position: mutation.position,
        };

      case 'resize-widget':

        return {
          type: 'resize',
          widgetInstanceId: mutation.widgetInstanceId,
          columnSpan: mutation.columnSpan,
          rowSpan: mutation.rowSpan,
        };

      case 'insert-widget':

        return {
          type: 'insert',
          widget: mutation.widget,
        };

      case 'remove-widget':

        return {
          type: 'remove',
          widgetInstanceId: mutation.widgetInstanceId,
        };

    }

  }

}