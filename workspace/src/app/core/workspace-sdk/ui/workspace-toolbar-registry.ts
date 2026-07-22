import {
  WorkspaceToolbar,
  WorkspaceToolbarId,
} from './workspace-toolbar';

/**
 * Erro lançado quando uma Toolbar duplicada é registrada.
 */
export class WorkspaceToolbarDuplicateError extends Error {
  constructor(readonly toolbarId: WorkspaceToolbarId) {
    super(`Workspace toolbar already registered: ${toolbarId}`);
    this.name = 'WorkspaceToolbarDuplicateError';
  }
}

/**
 * Erro lançado quando uma Toolbar não existe.
 */
export class WorkspaceToolbarNotFoundError extends Error {
  constructor(readonly toolbarId: WorkspaceToolbarId) {
    super(`Workspace toolbar not found: ${toolbarId}`);
    this.name = 'WorkspaceToolbarNotFoundError';
  }
}

/**
 * Registry oficial das Workspace Toolbars.
 */
export class WorkspaceToolbarRegistry {

  private readonly toolbars = new Map<
    WorkspaceToolbarId,
    WorkspaceToolbar
  >();

  /**
   * Registra uma Toolbar.
   */
  register(toolbar: WorkspaceToolbar): void {

    if (this.toolbars.has(toolbar.id)) {
      throw new WorkspaceToolbarDuplicateError(toolbar.id);
    }

    this.toolbars.set(toolbar.id, toolbar);
  }

  /**
   * Registra múltiplas Toolbars.
   */
  registerMany(toolbars: readonly WorkspaceToolbar[]): void {

    for (const toolbar of toolbars) {
      this.register(toolbar);
    }
  }

  /**
   * Remove uma Toolbar.
   */
  unregister(toolbarId: WorkspaceToolbarId): boolean {
    return this.toolbars.delete(toolbarId);
  }

  /**
   * Obtém uma Toolbar.
   */
  get(toolbarId: WorkspaceToolbarId): WorkspaceToolbar {

    const toolbar = this.toolbars.get(toolbarId);

    if (!toolbar) {
      throw new WorkspaceToolbarNotFoundError(toolbarId);
    }

    return toolbar;
  }

  /**
   * Verifica se uma Toolbar existe.
   */
  has(toolbarId: WorkspaceToolbarId): boolean {
    return this.toolbars.has(toolbarId);
  }

  /**
   * Lista todas as Toolbars ordenadas.
   */
  list(): readonly WorkspaceToolbar[] {

    return [...this.toolbars.values()]
      .sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
  }

  /**
   * Remove todas as Toolbars.
   */
  clear(): void {
    this.toolbars.clear();
  }

  /**
   * Quantidade de Toolbars registradas.
   */
  get size(): number {
    return this.toolbars.size;
  }

}