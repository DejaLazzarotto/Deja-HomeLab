/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Hook Registry
 *
 * Registry institucional responsável pelo gerenciamento dos
 * Hooks do ciclo de vida do Workspace Layout.
 */

import {
  WorkspaceLayoutHooks,
} from './workspace-layout-hooks';

/**
 * Identificador institucional de um ponto de Hook de Layout.
 */
export type WorkspaceLayoutHookName = keyof WorkspaceLayoutHooks;

/**
 * Registry institucional de Workspace Layout Hooks.
 */
export class WorkspaceLayoutHookRegistry {

  private readonly hooks = new Map<
    WorkspaceLayoutHookName,
    Array<NonNullable<WorkspaceLayoutHooks[WorkspaceLayoutHookName]>>
  >();

  /**
   * Registra um Hook preservando a ordem de inclusão.
   */
  register<K extends WorkspaceLayoutHookName>(
    hookName: K,
    hook: NonNullable<WorkspaceLayoutHooks[K]>,
  ): void {

    const hooks = this.hooks.get(hookName) ?? [];

    hooks.push(
      hook as NonNullable<
        WorkspaceLayoutHooks[WorkspaceLayoutHookName]
      >,
    );

    this.hooks.set(hookName, hooks);

  }

  /**
   * Remove uma ocorrência específica de um Hook.
   */
  unregister<K extends WorkspaceLayoutHookName>(
    hookName: K,
    hook: NonNullable<WorkspaceLayoutHooks[K]>,
  ): boolean {

    const hooks = this.hooks.get(hookName);

    if (!hooks) {
      return false;
    }

    const index = hooks.indexOf(
      hook as NonNullable<
        WorkspaceLayoutHooks[WorkspaceLayoutHookName]
      >,
    );

    if (index < 0) {
      return false;
    }

    hooks.splice(index, 1);

    if (hooks.length === 0) {
      this.hooks.delete(hookName);
    }

    return true;

  }

  /**
   * Obtém os Hooks registrados para um ponto do ciclo de vida.
   */
  get<K extends WorkspaceLayoutHookName>(
    hookName: K,
  ): ReadonlyArray<NonNullable<WorkspaceLayoutHooks[K]>> {

    return (
      this.hooks.get(hookName) ?? []
    ) as Array<NonNullable<WorkspaceLayoutHooks[K]>>;

  }

  /**
   * Verifica se existem Hooks registrados.
   */
  has(hookName: WorkspaceLayoutHookName): boolean {

    return (this.hooks.get(hookName)?.length ?? 0) > 0;

  }

  /**
   * Remove todos os Hooks de um ponto específico.
   */
  removeAll(hookName: WorkspaceLayoutHookName): boolean {

    return this.hooks.delete(hookName);

  }

  /**
   * Remove todos os Hooks registrados.
   */
  clear(): void {

    this.hooks.clear();

  }

}