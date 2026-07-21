import {
  WorkspaceRuntimeHook,
  WorkspaceRuntimeHookContext,
  WorkspaceRuntimeHookName,
} from './workspace-runtime-hooks';

/**
 * Dispatcher oficial de hooks do Workspace Runtime.
 *
 * Responsabilidades:
 * - registrar hooks;
 * - remover hooks;
 * - executar hooks em ordem determinística;
 * - suportar execução síncrona e assíncrona;
 * - permitir limpeza seletiva ou completa.
 */
export class WorkspaceRuntimeHookDispatcher {
  private readonly hooks = new Map<
    WorkspaceRuntimeHookName,
    WorkspaceRuntimeHook[]
  >();

  register(
    hookName: WorkspaceRuntimeHookName,
    hook: WorkspaceRuntimeHook,
  ): () => void {
    const registeredHooks = this.hooks.get(hookName) ?? [];

    registeredHooks.push(hook);
    this.hooks.set(hookName, registeredHooks);

    return () => {
      this.unregister(hookName, hook);
    };
  }

  unregister(
    hookName: WorkspaceRuntimeHookName,
    hook: WorkspaceRuntimeHook,
  ): boolean {
    const registeredHooks = this.hooks.get(hookName);

    if (!registeredHooks) {
      return false;
    }

    const hookIndex = registeredHooks.indexOf(hook);

    if (hookIndex < 0) {
      return false;
    }

    registeredHooks.splice(hookIndex, 1);

    if (registeredHooks.length === 0) {
      this.hooks.delete(hookName);
    }

    return true;
  }

  async execute(
    hookName: WorkspaceRuntimeHookName,
    context: WorkspaceRuntimeHookContext,
  ): Promise<void> {
    const registeredHooks = [
      ...(this.hooks.get(hookName) ?? []),
    ];

    for (const hook of registeredHooks) {
      await hook(context);
    }
  }

  count(hookName: WorkspaceRuntimeHookName): number {
    return this.hooks.get(hookName)?.length ?? 0;
  }

  clear(hookName?: WorkspaceRuntimeHookName): void {
    if (hookName) {
      this.hooks.delete(hookName);
      return;
    }

    this.hooks.clear();
  }
}