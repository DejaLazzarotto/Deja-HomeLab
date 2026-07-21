import {
  WorkspaceRuntimeContext,
} from '../models/workspace-models';

/**
 * Contexto disponibilizado aos hooks do Workspace Runtime.
 */
export interface WorkspaceRuntimeHookContext {
  readonly runtimeContext?: WorkspaceRuntimeContext;
  readonly operation: string;
  readonly data?: Readonly<Record<string, unknown>>;
}

/**
 * Hook oficial do Workspace Runtime.
 */
export type WorkspaceRuntimeHook = (
  context: WorkspaceRuntimeHookContext,
) => void | Promise<void>;

/**
 * Nomes oficiais dos hooks do ciclo de vida do Workspace Runtime.
 */
export const WorkspaceRuntimeHooks = {
  BeforeInitialize: 'runtime.beforeInitialize',
  AfterInitialize: 'runtime.afterInitialize',

  BeforeStart: 'runtime.beforeStart',
  AfterStart: 'runtime.afterStart',

  BeforeStop: 'runtime.beforeStop',
  AfterStop: 'runtime.afterStop',

  BeforeReset: 'runtime.beforeReset',
  AfterReset: 'runtime.afterReset',
} as const;

/**
 * Nome válido de hook do Workspace Runtime.
 */
export type WorkspaceRuntimeHookName =
  (typeof WorkspaceRuntimeHooks)[keyof typeof WorkspaceRuntimeHooks];