/*
 * Deja Workspace UI SDK
 *
 * Workspace Command Palette Registry
 *
 * Registry oficial responsável pelo gerenciamento dos itens
 * institucionais da Command Palette do Workspace.
 */

import {
  WorkspaceCommandPalette,
  WorkspaceCommandPaletteId,
} from './workspace-command-palette';

/**
 * Erro lançado quando um item duplicado é registrado.
 */
export class WorkspaceCommandPaletteDuplicateError extends Error {
  constructor(readonly paletteId: WorkspaceCommandPaletteId) {
    super(`Workspace command palette item already registered: ${paletteId}`);
    this.name = 'WorkspaceCommandPaletteDuplicateError';
  }
}

/**
 * Erro lançado quando um item não existe.
 */
export class WorkspaceCommandPaletteNotFoundError extends Error {
  constructor(readonly paletteId: WorkspaceCommandPaletteId) {
    super(`Workspace command palette item not found: ${paletteId}`);
    this.name = 'WorkspaceCommandPaletteNotFoundError';
  }
}

/**
 * Registry oficial da Workspace Command Palette.
 */
export class WorkspaceCommandPaletteRegistry {

  private readonly items = new Map<
    WorkspaceCommandPaletteId,
    WorkspaceCommandPalette
  >();

  /**
   * Registra um item.
   */
  register(
    item: WorkspaceCommandPalette,
  ): void {

    if (this.items.has(item.id)) {
      throw new WorkspaceCommandPaletteDuplicateError(item.id);
    }

    this.items.set(item.id, item);
  }

  /**
   * Registra múltiplos itens.
   */
  registerMany(
    items: readonly WorkspaceCommandPalette[],
  ): void {

    for (const item of items) {
      this.register(item);
    }
  }

  /**
   * Remove um item.
   */
  unregister(
    paletteId: WorkspaceCommandPaletteId,
  ): boolean {

    return this.items.delete(paletteId);
  }

  /**
   * Remove todos os itens.
   */
  clear(): void {
    this.items.clear();
  }

  /**
   * Verifica se um item existe.
   */
  has(
    paletteId: WorkspaceCommandPaletteId,
  ): boolean {

    return this.items.has(paletteId);
  }

  /**
   * Obtém um item.
   */
  get(
    paletteId: WorkspaceCommandPaletteId,
  ): WorkspaceCommandPalette {

    const item = this.items.get(paletteId);

    if (!item) {
      throw new WorkspaceCommandPaletteNotFoundError(paletteId);
    }

    return item;
  }

  /**
   * Retorna todos os itens ordenados.
   */
  getAll(): readonly WorkspaceCommandPalette[] {

    return [...this.items.values()].sort((left, right) => {
      return (left.order ?? 0) - (right.order ?? 0);
    });
  }

  /**
   * Pesquisa itens da Command Palette.
   *
   * A pesquisa considera:
   * - título;
   * - descrição;
   * - categoria;
   * - palavras-chave.
   */
  search(
    text: string,
  ): readonly WorkspaceCommandPalette[] {

    const query = text.trim().toLowerCase();

    if (!query) {
      return this.getAll();
    }

    return this.getAll().filter(item => {

      const searchableValues = [
        item.title,
        item.description,
        item.category,
        ...(item.keywords ?? []),
      ];

      return searchableValues.some(value =>
        value?.toLowerCase().includes(query),
      );
    });
  }

  /**
   * Quantidade de itens registrados.
   */
  get size(): number {
    return this.items.size;
  }
}