/*
 * Deja Workspace UI SDK
 *
 * Workspace Context Menu Registry
 *
 * Registry oficial responsável pelo gerenciamento dos
 * Context Menus institucionais do Workspace.
 */

import {
  WorkspaceContextMenu,
  WorkspaceContextMenuId,
} from './workspace-context-menu';

/**
 * Erro lançado quando um Context Menu duplicado é registrado.
 */
export class WorkspaceContextMenuDuplicateError extends Error {
  constructor(readonly contextMenuId: WorkspaceContextMenuId) {
    super(`Workspace Context Menu already registered: ${contextMenuId}`);
    this.name = 'WorkspaceContextMenuDuplicateError';
  }
}

/**
 * Erro lançado quando um Context Menu não existe.
 */
export class WorkspaceContextMenuNotFoundError extends Error {
  constructor(readonly contextMenuId: WorkspaceContextMenuId) {
    super(`Workspace Context Menu not found: ${contextMenuId}`);
    this.name = 'WorkspaceContextMenuNotFoundError';
  }
}

/**
 * Registry oficial de Workspace Context Menus.
 */
export class WorkspaceContextMenuRegistry {

  private readonly contextMenus = new Map<
    WorkspaceContextMenuId,
    WorkspaceContextMenu
  >();

  /**
   * Registra um Context Menu.
   */
  register(contextMenu: WorkspaceContextMenu): void {

    if (this.contextMenus.has(contextMenu.id)) {
      throw new WorkspaceContextMenuDuplicateError(contextMenu.id);
    }

    this.contextMenus.set(contextMenu.id, contextMenu);
  }

  /**
   * Registra múltiplos Context Menus.
   */
  registerMany(
    contextMenus: readonly WorkspaceContextMenu[],
  ): void {

    for (const contextMenu of contextMenus) {
      this.register(contextMenu);
    }
  }

  /**
   * Remove um Context Menu.
   */
  unregister(
    contextMenuId: WorkspaceContextMenuId,
  ): boolean {

    return this.contextMenus.delete(contextMenuId);
  }

  /**
   * Remove todos os Context Menus.
   */
  clear(): void {
    this.contextMenus.clear();
  }

  /**
   * Verifica se um Context Menu existe.
   */
  has(
    contextMenuId: WorkspaceContextMenuId,
  ): boolean {

    return this.contextMenus.has(contextMenuId);
  }

  /**
   * Obtém um Context Menu.
   */
  get(
    contextMenuId: WorkspaceContextMenuId,
  ): WorkspaceContextMenu {

    const contextMenu = this.contextMenus.get(contextMenuId);

    if (!contextMenu) {
      throw new WorkspaceContextMenuNotFoundError(contextMenuId);
    }

    return contextMenu;
  }

  /**
   * Retorna todos os Context Menus ordenados.
   */
  getAll(): readonly WorkspaceContextMenu[] {

    return [...this.contextMenus.values()].sort((left, right) => {
      return (left.order ?? 0) - (right.order ?? 0);
    });
  }

  /**
   * Quantidade de Context Menus registrados.
   */
  get size(): number {
    return this.contextMenus.size;
  }
}