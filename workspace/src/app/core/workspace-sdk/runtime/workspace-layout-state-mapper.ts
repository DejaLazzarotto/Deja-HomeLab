/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout State Mapper
 *
 * Infraestrutura institucional responsável pela transformação
 * entre Dashboards resolvidos e estados persistíveis de Layout.
 */

import {
  WorkspaceLayoutState,
} from './workspace-layout-state';

import {
  WorkspaceResolvedDashboard,
} from './workspace-resolved-dashboard';

import {
  WorkspaceGridPosition,
  WorkspaceWidgetInstance,
} from './workspace-widget';

/**
 * Infraestrutura institucional responsável pela conversão entre
 * o modelo de Runtime e o estado serializável de Layout.
 *
 * O Mapper permanece completamente independente de mecanismos
 * de armazenamento, Angular, APIs remotas ou bibliotecas visuais.
 */
export class WorkspaceLayoutStateMapper {

  /**
   * Versão atual do contrato institucional de persistência.
   */
  private static readonly currentVersion = 1;

  /**
   * Produz um estado persistível a partir de um Dashboard resolvido.
   *
   * Dashboards sem Layout institucional não podem produzir um
   * WorkspaceLayoutState e retornam undefined.
   */
  static fromResolvedDashboard(
    dashboard: WorkspaceResolvedDashboard,
  ): WorkspaceLayoutState | undefined {

    if (!dashboard.layout) {
      return undefined;
    }

    return {
      dashboardId: dashboard.dashboard.id,
      layoutId: dashboard.layout.id,
      version: this.currentVersion,
      widgets: dashboard.widgets.map(
        widget => this.cloneWidget(widget),
      ),
      configuration:
        dashboard.state?.configuration
          ? {
              ...dashboard.state.configuration,
            }
          : undefined,
      metadata:
        dashboard.state?.metadata
          ? {
              ...dashboard.state.metadata,
            }
          : undefined,
    };

  }

  /**
   * Aplica um estado persistido sobre um Dashboard resolvido.
   *
   * O Dashboard recebido permanece imutável.
   *
   * Estados pertencentes a outro Dashboard ou outro Layout são
   * ignorados, preservando integralmente o Dashboard recebido.
   */
  static applyState(
    dashboard: WorkspaceResolvedDashboard,
    state: WorkspaceLayoutState,
  ): WorkspaceResolvedDashboard {

    if (state.dashboardId !== dashboard.dashboard.id) {
      return dashboard;
    }

    if (
      dashboard.layout
      && state.layoutId !== dashboard.layout.id
    ) {
      return dashboard;
    }

    return {
      ...dashboard,
      widgets:
        state.widgets
          ? state.widgets.map(
              widget => this.cloneWidget(widget),
            )
          : dashboard.widgets,
      state: this.cloneState(state),
    };

  }

  /**
   * Cria uma cópia imutável de um estado persistido.
   */
  private static cloneState(
    state: WorkspaceLayoutState,
  ): WorkspaceLayoutState {

    return {
      dashboardId: state.dashboardId,
      layoutId: state.layoutId,
      version: state.version,
      widgets:
        state.widgets
          ? state.widgets.map(
              widget => this.cloneWidget(widget),
            )
          : undefined,
      configuration:
        state.configuration
          ? {
              ...state.configuration,
            }
          : undefined,
      metadata:
        state.metadata
          ? {
              ...state.metadata,
            }
          : undefined,
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

}