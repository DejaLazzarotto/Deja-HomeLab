/*
 * Deja Workspace UI SDK
 *
 * Workspace Widget Registry
 *
 * Registry oficial responsável pelo gerenciamento dos Widgets
 * institucionais do Workspace.
 */

import {
  WorkspaceWidget,
} from './workspace-widget';

import {
  WorkspaceActionId,
} from './workspace-action';

import {
  WorkspaceWidgetCapability,
  WorkspaceWidgetCategory,
  WorkspaceWidgetId,
  WorkspaceWidgetSurface,
} from '../contracts/workspace-contracts';

/**
 * Erro lançado quando um Widget duplicado é registrado.
 */
export class WorkspaceWidgetDuplicateError extends Error {

  constructor(readonly widgetId: WorkspaceWidgetId) {

    super(`Workspace widget already registered: ${widgetId}`);

    this.name = 'WorkspaceWidgetDuplicateError';
  }

}

/**
 * Erro lançado quando um Widget não existe.
 */
export class WorkspaceWidgetNotFoundError extends Error {

  constructor(readonly widgetId: WorkspaceWidgetId) {

    super(`Workspace widget not found: ${widgetId}`);

    this.name = 'WorkspaceWidgetNotFoundError';
  }

}

/**
 * Registry institucional de Workspace Widgets.
 */
export class WorkspaceWidgetRegistry {

  private readonly widgets = new Map<WorkspaceWidgetId, WorkspaceWidget>();

  /**
   * Registra um Widget.
   */
  register(widget: WorkspaceWidget): void {

    if (this.widgets.has(widget.id)) {
      throw new WorkspaceWidgetDuplicateError(widget.id);
    }

    this.widgets.set(widget.id, widget);

  }

  /**
   * Registra múltiplos Widgets.
   */
  registerMany(
    widgets: readonly WorkspaceWidget[],
  ): void {

    widgets.forEach((widget) => this.register(widget));

  }

  /**
   * Remove um Widget.
   */
  unregister(
    widgetId: WorkspaceWidgetId,
  ): boolean {

    return this.widgets.delete(widgetId);

  }

  /**
   * Remove todos os Widgets.
   */
  clear(): void {

    this.widgets.clear();

  }

  /**
   * Obtém um Widget.
   */
  get(
    widgetId: WorkspaceWidgetId,
  ): WorkspaceWidget {

    const widget = this.widgets.get(widgetId);

    if (!widget) {
      throw new WorkspaceWidgetNotFoundError(widgetId);
    }

    return widget;

  }

  /**
   * Verifica se um Widget existe.
   */
  has(
    widgetId: WorkspaceWidgetId,
  ): boolean {

    return this.widgets.has(widgetId);

  }

  /**
   * Retorna todos os Widgets.
   */
  getAll(): readonly WorkspaceWidget[] {

    return [...this.widgets.values()];

  }

  /**
   * Retorna Widgets habilitados.
   */
  getEnabled(): readonly WorkspaceWidget[] {

    return this.getAll().filter((widget) => widget.enabled !== false);

  }

  /**
   * Consulta Widgets por categoria.
   */
  getByCategory(
    category: WorkspaceWidgetCategory,
  ): readonly WorkspaceWidget[] {

    return this.getAll().filter(
      (widget) => widget.category === category,
    );

  }

  /**
   * Consulta Widgets por superfície.
   */
  getBySurface(
    surface: WorkspaceWidgetSurface,
  ): readonly WorkspaceWidget[] {

    return this.getAll().filter(
      (widget) => widget.supportedSurfaces?.includes(surface),
    );

  }

  /**
   * Consulta Widgets por capacidade.
   */
  getByCapability(
    capability: WorkspaceWidgetCapability,
  ): readonly WorkspaceWidget[] {

    return this.getAll().filter(
      (widget) => widget.capabilities?.includes(capability),
    );

  }

  /**
   * Consulta Widgets por Action.
   */
  getByAction(
    actionId: WorkspaceActionId,
  ): readonly WorkspaceWidget[] {

    return this.getAll().filter((widget) =>

      widget.primaryActionId === actionId
      || widget.actionIds?.includes(actionId),

    );

  }

  /**
   * Quantidade de Widgets registrados.
   */
  size(): number {

    return this.widgets.size;

  }

}