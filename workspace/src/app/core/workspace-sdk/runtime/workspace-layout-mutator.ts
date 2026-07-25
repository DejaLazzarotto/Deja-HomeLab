/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Mutator
 *
 * Infraestrutura institucional responsável pela aplicação de
 * mutações estruturadas sobre Dashboards resolvidos do Workspace.
 */

import {
  WorkspaceInsertWidgetMutation,
  WorkspaceLayoutMutationOperation,
  WorkspaceLayoutMutationResult,
  WorkspaceMoveWidgetMutation,
  WorkspaceRemoveWidgetMutation,
  WorkspaceResizeWidgetMutation,
} from './workspace-layout-mutation';

import {
  WorkspaceResolvedDashboard,
} from './workspace-resolved-dashboard';

import {
  WorkspaceGridPosition,
  WorkspaceWidgetInstance,
} from './workspace-widget';

/**
 * Infraestrutura institucional responsável pelas mutações
 * estruturadas dos Layouts do Workspace.
 *
 * Todas as operações são aplicadas de forma imutável, produzindo
 * um novo WorkspaceResolvedDashboard sem alterar o modelo recebido.
 *
 * O Mutator permanece completamente independente de Angular,
 * mecanismos de Drag-and-Drop, bibliotecas visuais ou persistência.
 */
export class WorkspaceLayoutMutator {

  /**
   * Aplica uma mutação estrutural sobre um Dashboard resolvido.
   */
  static mutate(
    dashboard: WorkspaceResolvedDashboard,
    mutation: WorkspaceLayoutMutationOperation,
  ): WorkspaceLayoutMutationResult {

    switch (mutation.type) {

      case 'move-widget':
        return this.moveWidget(
          dashboard,
          mutation,
        );

      case 'resize-widget':
        return this.resizeWidget(
          dashboard,
          mutation,
        );

      case 'insert-widget':
        return this.insertWidget(
          dashboard,
          mutation,
        );

      case 'remove-widget':
        return this.removeWidget(
          dashboard,
          mutation,
        );

      default:
        return this.assertNever(mutation);

    }

  }

  /**
   * Aplica a movimentação de uma instância de Widget.
   */
  private static moveWidget(
    dashboard: WorkspaceResolvedDashboard,
    mutation: WorkspaceMoveWidgetMutation,
  ): WorkspaceLayoutMutationResult {

    const widget = this.findWidget(
      dashboard,
      mutation.widgetInstanceId,
    );

    if (!widget) {
      return this.createRejectedResult(
        dashboard,
        mutation,
        `Workspace widget instance not found: ${mutation.widgetInstanceId}`,
      );
    }

    const positionDiagnostic = this.validatePosition(
      mutation.position,
    );

    if (positionDiagnostic) {
      return this.createRejectedResult(
        dashboard,
        mutation,
        positionDiagnostic,
      );
    }

    if (
      mutation.regionId !== undefined
      && !this.regionExists(
        dashboard,
        mutation.regionId,
      )
    ) {
      return this.createRejectedResult(
        dashboard,
        mutation,
        `Workspace layout region not found: ${mutation.regionId}`,
      );
    }

    const widgets: readonly WorkspaceWidgetInstance[] =
      dashboard.widgets.map(
        currentWidget => {

          if (currentWidget.id !== mutation.widgetInstanceId) {
            return currentWidget;
          }

          return {
            ...currentWidget,
            regionId:
              mutation.regionId
              ?? currentWidget.regionId,
            position: this.clonePosition(
              mutation.position,
            ),
          };

        },
      );

    return this.createAppliedResult(
      dashboard,
      mutation,
      widgets,
    );

  }

  /**
   * Aplica o redimensionamento de uma instância de Widget.
   */
  private static resizeWidget(
    dashboard: WorkspaceResolvedDashboard,
    mutation: WorkspaceResizeWidgetMutation,
  ): WorkspaceLayoutMutationResult {

    const widget = this.findWidget(
      dashboard,
      mutation.widgetInstanceId,
    );

    if (!widget) {
      return this.createRejectedResult(
        dashboard,
        mutation,
        `Workspace widget instance not found: ${mutation.widgetInstanceId}`,
      );
    }

    if (
      mutation.columnSpan === undefined
      && mutation.rowSpan === undefined
    ) {
      return this.createRejectedResult(
        dashboard,
        mutation,
        'Workspace resize mutation requires columnSpan or rowSpan.',
      );
    }

    if (
      mutation.columnSpan !== undefined
      && mutation.columnSpan < 1
    ) {
      return this.createRejectedResult(
        dashboard,
        mutation,
        'Workspace widget columnSpan must be greater than zero.',
      );
    }

    if (
      mutation.rowSpan !== undefined
      && mutation.rowSpan < 1
    ) {
      return this.createRejectedResult(
        dashboard,
        mutation,
        'Workspace widget rowSpan must be greater than zero.',
      );
    }

    if (!widget.position) {
      return this.createRejectedResult(
        dashboard,
        mutation,
        `Workspace widget instance has no grid position: ${mutation.widgetInstanceId}`,
      );
    }

    const widgets: readonly WorkspaceWidgetInstance[] =
      dashboard.widgets.map(
        currentWidget => {

          if (currentWidget.id !== mutation.widgetInstanceId) {
            return currentWidget;
          }

          if (!currentWidget.position) {
            return currentWidget;
          }

          const currentPosition = currentWidget.position;

          const position: WorkspaceGridPosition = {
            column: currentPosition.column,
            row: currentPosition.row,
            columnSpan:
              mutation.columnSpan
              ?? currentPosition.columnSpan,
            rowSpan:
              mutation.rowSpan
              ?? currentPosition.rowSpan,
          };

          return {
            ...currentWidget,
            position,
          };

        },
      );

    return this.createAppliedResult(
      dashboard,
      mutation,
      widgets,
    );

  }

  /**
   * Insere uma nova instância de Widget no Dashboard.
   */
  private static insertWidget(
    dashboard: WorkspaceResolvedDashboard,
    mutation: WorkspaceInsertWidgetMutation,
  ): WorkspaceLayoutMutationResult {

    if (
      dashboard.widgets.some(
        widget => widget.id === mutation.widget.id,
      )
    ) {
      return this.createRejectedResult(
        dashboard,
        mutation,
        `Workspace widget instance already exists: ${mutation.widget.id}`,
      );
    }

    if (
      mutation.widget.regionId !== undefined
      && !this.regionExists(
        dashboard,
        mutation.widget.regionId,
      )
    ) {
      return this.createRejectedResult(
        dashboard,
        mutation,
        `Workspace layout region not found: ${mutation.widget.regionId}`,
      );
    }

    if (mutation.widget.position) {

      const positionDiagnostic = this.validatePosition(
        mutation.widget.position,
      );

      if (positionDiagnostic) {
        return this.createRejectedResult(
          dashboard,
          mutation,
          positionDiagnostic,
        );
      }

    }

    const widgets: readonly WorkspaceWidgetInstance[] = [
      ...dashboard.widgets,
      this.cloneWidget(mutation.widget),
    ];

    return this.createAppliedResult(
      dashboard,
      mutation,
      widgets,
    );

  }

  /**
   * Remove uma instância de Widget do Dashboard.
   */
  private static removeWidget(
    dashboard: WorkspaceResolvedDashboard,
    mutation: WorkspaceRemoveWidgetMutation,
  ): WorkspaceLayoutMutationResult {

    const widget = this.findWidget(
      dashboard,
      mutation.widgetInstanceId,
    );

    if (!widget) {
      return this.createRejectedResult(
        dashboard,
        mutation,
        `Workspace widget instance not found: ${mutation.widgetInstanceId}`,
      );
    }

    const widgets: readonly WorkspaceWidgetInstance[] =
      dashboard.widgets.filter(
        currentWidget =>
          currentWidget.id !== mutation.widgetInstanceId,
      );

    return this.createAppliedResult(
      dashboard,
      mutation,
      widgets,
    );

  }

  /**
   * Localiza uma instância de Widget no Dashboard.
   */
  private static findWidget(
    dashboard: WorkspaceResolvedDashboard,
    widgetInstanceId: string,
  ): WorkspaceWidgetInstance | undefined {

    return dashboard.widgets.find(
      widget => widget.id === widgetInstanceId,
    );

  }

  /**
   * Verifica se uma região pertence ao Dashboard resolvido.
   */
  private static regionExists(
    dashboard: WorkspaceResolvedDashboard,
    regionId: WorkspaceWidgetInstance['regionId'],
  ): boolean {

    return dashboard.regions.some(
      region => region.id === regionId,
    );

  }

  /**
   * Valida uma posição declarativa de Grid.
   */
  private static validatePosition(
    position: WorkspaceGridPosition,
  ): string | undefined {

    if (position.column < 1) {
      return 'Workspace widget column must be greater than zero.';
    }

    if (position.row < 1) {
      return 'Workspace widget row must be greater than zero.';
    }

    if (
      position.columnSpan !== undefined
      && position.columnSpan < 1
    ) {
      return 'Workspace widget columnSpan must be greater than zero.';
    }

    if (
      position.rowSpan !== undefined
      && position.rowSpan < 1
    ) {
      return 'Workspace widget rowSpan must be greater than zero.';
    }

    return undefined;

  }

  /**
   * Cria uma cópia imutável de uma posição declarativa.
   */
  private static clonePosition(
    position: WorkspaceGridPosition,
  ): WorkspaceGridPosition {

    return {
      column: position.column,
      row: position.row,
      columnSpan: position.columnSpan,
      rowSpan: position.rowSpan,
    };

  }

  /**
   * Cria uma cópia imutável de uma instância de Widget.
   */
  private static cloneWidget(
    widget: WorkspaceWidgetInstance,
  ): WorkspaceWidgetInstance {

    return {
      ...widget,
      position:
        widget.position
          ? this.clonePosition(widget.position)
          : undefined,
      configuration:
        widget.configuration
          ? {
              ...widget.configuration,
            }
          : undefined,
    };

  }

  /**
   * Produz um novo Dashboard resolvido com a coleção atualizada
   * de Widgets.
   */
  private static cloneDashboard(
    dashboard: WorkspaceResolvedDashboard,
    widgets: readonly WorkspaceWidgetInstance[],
  ): WorkspaceResolvedDashboard {

    return {
      ...dashboard,
      widgets,
    };

  }

  /**
   * Cria o resultado de uma mutação aplicada.
   */
  private static createAppliedResult(
    dashboard: WorkspaceResolvedDashboard,
    mutation: WorkspaceLayoutMutationOperation,
    widgets: readonly WorkspaceWidgetInstance[],
  ): WorkspaceLayoutMutationResult {

    return {
      mutation,
      applied: true,
      dashboard: this.cloneDashboard(
        dashboard,
        widgets,
      ),
      diagnostics: [],
    };

  }

  /**
   * Cria o resultado de uma mutação rejeitada.
   */
  private static createRejectedResult(
    dashboard: WorkspaceResolvedDashboard,
    mutation: WorkspaceLayoutMutationOperation,
    diagnostic: string,
  ): WorkspaceLayoutMutationResult {

    return {
      mutation,
      applied: false,
      dashboard,
      diagnostics: [
        diagnostic,
      ],
    };

  }

  /**
   * Garante despacho exaustivo das mutações institucionais.
   */
  private static assertNever(
    mutation: never,
  ): never {

    throw new Error(
      `Unsupported workspace layout mutation: ${JSON.stringify(mutation)}`,
    );

  }

}