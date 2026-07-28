/*
 * Deja Workspace UI
 *
 * Workspace Render Strategy Factory
 *
 * Factory institucional responsável pela composição e
 * resolução das estratégias de renderização do Workspace.
 */

import {
  WorkspaceIncrementalRenderExecutor,
} from '../../core/workspace-sdk/runtime/workspace-incremental-render-executor';

import {
  WorkspaceIncrementalRenderOperationFactory,
} from '../../core/workspace-sdk/runtime/workspace-incremental-render-operation-factory';

import {
  WorkspaceWidgetReferenceRegistry,
} from '../../core/workspace-sdk/runtime/workspace-widget-reference-registry';

import {
  AngularWorkspaceWidgetRenderAdapter,
} from './angular-workspace-widget-render-adapter';

import {
  WorkspaceFullRenderStrategy,
} from './workspace-full-render-strategy';

import {
  WorkspaceIncrementalRenderStrategy,
} from './workspace-incremental-render-strategy';

import {
  WorkspaceRenderStrategy,
} from './workspace-render-strategy';

/**
 * Factory responsável pela composição e resolução das
 * estratégias de renderização do Workspace.
 *
 * A composição recebe apenas o contrato institucional de
 * localização de Widgets renderizados, permanecendo
 * desacoplada da implementação concreta do cache Angular.
 */
export class WorkspaceRenderStrategyFactory {

  private readonly fullRenderStrategy:
    WorkspaceFullRenderStrategy;

  private readonly incrementalRenderStrategy:
    WorkspaceIncrementalRenderStrategy;

  constructor(
    widgetReferenceRegistry:
      WorkspaceWidgetReferenceRegistry,
  ) {

    this.fullRenderStrategy =
      new WorkspaceFullRenderStrategy();

    const operationFactory =
      new WorkspaceIncrementalRenderOperationFactory();

    const widgetRenderAdapter =
      new AngularWorkspaceWidgetRenderAdapter(
        widgetReferenceRegistry,
      );

    const executor =
      new WorkspaceIncrementalRenderExecutor(
        widgetRenderAdapter,
      );

    this.incrementalRenderStrategy =
      new WorkspaceIncrementalRenderStrategy(
        operationFactory,
        executor,
        this.fullRenderStrategy,
      );

  }

  /**
   * Resolve a estratégia institucional de renderização.
   */
  create(): WorkspaceRenderStrategy {

    return this.incrementalRenderStrategy;

  }

}