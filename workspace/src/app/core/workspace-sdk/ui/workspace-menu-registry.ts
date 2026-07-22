/*
 * Deja Workspace UI SDK
 *
 * Workspace Menu Registry
 *
 * Registry oficial responsável pelo gerenciamento dos menus
 * institucionais do Workspace.
 */

import {
  WorkspaceMenu,
  WorkspaceMenuId,
  WorkspaceMenuLocation,
} from './workspace-menu';

/**
 * Erro lançado quando um menu duplicado é registrado.
 */
export class WorkspaceMenuDuplicateError extends Error {
  constructor(readonly menuId: WorkspaceMenuId) {
    super(`Workspace menu already registered: ${menuId}`);
    this.name = 'WorkspaceMenuDuplicateError';
  }
}

/**
 * Erro lançado quando um menu não existe.
 */
export class WorkspaceMenuNotFoundError extends Error {
  constructor(readonly menuId: WorkspaceMenuId) {
    super(`Workspace menu not found: ${menuId}`);
    this.name = 'WorkspaceMenuNotFoundError';
  }
}

/**
 * Registry oficial de Workspace Menus.
 */
export class WorkspaceMenuRegistry {

  private readonly menus = new Map<WorkspaceMenuId, WorkspaceMenu>();

  /**
   * Registra um menu.
   */
  register(menu: WorkspaceMenu): void {

    if (this.menus.has(menu.id)) {
      throw new WorkspaceMenuDuplicateError(menu.id);
    }

    this.menus.set(menu.id, menu);
  }

  /**
   * Registra múltiplos menus.
   */
  registerMany(
    menus: readonly WorkspaceMenu[],
  ): void {

    for (const menu of menus) {
      this.register(menu);
    }
  }

  /**
   * Remove um menu.
   */
  unregister(
    menuId: WorkspaceMenuId,
  ): boolean {

    return this.menus.delete(menuId);
  }

  /**
   * Remove todos os menus.
   */
  clear(): void {
    this.menus.clear();
  }

  /**
   * Verifica se um menu existe.
   */
  has(
    menuId: WorkspaceMenuId,
  ): boolean {

    return this.menus.has(menuId);
  }

  /**
   * Obtém um menu.
   */
  get(
    menuId: WorkspaceMenuId,
  ): WorkspaceMenu {

    const menu = this.menus.get(menuId);

    if (!menu) {
      throw new WorkspaceMenuNotFoundError(menuId);
    }

    return menu;
  }

  /**
   * Retorna todos os menus ordenados.
   */
  getAll(): readonly WorkspaceMenu[] {

    return [...this.menus.values()].sort((left, right) => {
      return (left.order ?? 0) - (right.order ?? 0);
    });
  }

  /**
   * Retorna todos os menus de uma localização.
   */
  getByLocation(
    location: WorkspaceMenuLocation,
  ): readonly WorkspaceMenu[] {

    return this.getAll().filter(menu =>
      menu.location === location,
    );
  }

  /**
   * Quantidade de menus registrados.
   */
  get size(): number {
    return this.menus.size;
  }
}