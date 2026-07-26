/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Hook Dispatcher
 *
 * Infraestrutura institucional responsável pela execução
 * ordenada dos Workspace Layout Hooks.
 */

import {
  WorkspaceLayoutHook,
} from './workspace-layout-hook';

import {
  WorkspaceLayoutHookName,
  WorkspaceLayoutHookRegistry,
} from './workspace-layout-hook-registry';

import {
  WorkspaceLayoutHooks,
} from './workspace-layout-hooks';

/**
 * Responsável pela execução institucional dos Hooks
 * registrados para o Workspace Layout.
 */
export class WorkspaceLayoutHookDispatcher {

  constructor(
    private readonly registry: WorkspaceLayoutHookRegistry,
  ) {}

  /**
   * Executa todos os Hooks registrados para um ponto
   * específico do ciclo de vida.
   */
  async dispatch<K extends WorkspaceLayoutHookName>(
    hookName: K,
    context: Parameters<
      NonNullable<WorkspaceLayoutHooks[K]>
    >[0],
  ): Promise<void> {

    type HookContext = Parameters<
      NonNullable<WorkspaceLayoutHooks[K]>
    >[0];

    const hooks = this.registry.get(hookName) as ReadonlyArray<
      WorkspaceLayoutHook<HookContext>
    >;

    for (const hook of hooks) {
      await hook(context);
    }

  }

}