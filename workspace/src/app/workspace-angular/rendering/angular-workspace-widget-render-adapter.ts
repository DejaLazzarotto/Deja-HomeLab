/*
 * Deja Workspace Angular Integration
 *
 * Angular Workspace Widget Render Adapter
 *
 * Implementação Angular do contrato institucional de
 * renderização incremental de Widgets.
 */

import {
  WorkspaceIncrementalRenderOperation,
  WorkspaceMoveRenderOperation,
  WorkspaceRemoveRenderOperation,
  WorkspaceResizeRenderOperation,
} from '../../core/workspace-sdk/runtime/workspace-incremental-render-operation';

import {
  WorkspaceWidgetReferenceRegistry,
} from '../../core/workspace-sdk/runtime/workspace-widget-reference-registry';

import {
  WorkspaceWidgetRenderAdapter,
} from '../../core/workspace-sdk/runtime/workspace-widget-render-adapter';

import {
  WorkspaceWidgetComponentReference,
} from './workspace-widget-component-reference';

/**
 * Implementação Angular responsável pela execução concreta
 * das operações incrementais de renderização de Widgets.
 *
 * O Adapter representa a fronteira entre o contrato
 * institucional do Workspace SDK e a infraestrutura Angular.
 */
export class AngularWorkspaceWidgetRenderAdapter
  implements WorkspaceWidgetRenderAdapter {

  constructor(
    private readonly registry:
      WorkspaceWidgetReferenceRegistry,
  ) {}

  /**
   * Executa a movimentação incremental de um Widget.
   */
  move(
    operation: WorkspaceIncrementalRenderOperation,
  ): boolean {

    if (operation.type !== 'move') {
      return false;
    }

    const moveOperation =
      operation as WorkspaceMoveRenderOperation;

    const reference = this.getReference(
      moveOperation.widgetInstanceId,
    );

    if (!reference) {
      return false;
    }

    return reference.controller.move();

  }

  /**
   * Executa o redimensionamento incremental de um Widget.
   */
  resize(
    operation: WorkspaceIncrementalRenderOperation,
  ): boolean {

    if (operation.type !== 'resize') {
      return false;
    }

    const resizeOperation =
      operation as WorkspaceResizeRenderOperation;

    const reference = this.getReference(
      resizeOperation.widgetInstanceId,
    );

    if (!reference) {
      return false;
    }

    return reference.controller.resize();

  }

  /**
   * Executa a inserção incremental de um Widget.
   *
   * Uma inserção ainda não possui referência registrada.
   * Por isso, permanece utilizando Full Render como fallback
   * até que exista uma infraestrutura Angular responsável
   * pela criação dinâmica do novo WorkspaceWidgetHostComponent.
   */
  insert(
    operation: WorkspaceIncrementalRenderOperation,
  ): boolean {

    if (operation.type !== 'insert') {
      return false;
    }

    return false;

  }

  /**
   * Executa a remoção incremental de um Widget.
   */
  remove(
    operation: WorkspaceIncrementalRenderOperation,
  ): boolean {

    if (operation.type !== 'remove') {
      return false;
    }

    const removeOperation =
      operation as WorkspaceRemoveRenderOperation;

    const reference = this.getReference(
      removeOperation.widgetInstanceId,
    );

    if (!reference) {
      return false;
    }

    return reference.controller.destroy();

  }

  /**
   * Resolve a referência Angular concreta associada ao
   * contrato institucional neutro do Workspace SDK.
   */
  private getReference(
    widgetInstanceId: string,
  ): WorkspaceWidgetComponentReference | undefined {

    return this.registry.get(
      widgetInstanceId,
    ) as WorkspaceWidgetComponentReference | undefined;

  }

}