/**
 * Eventos oficiais do ciclo de vida do Workspace Runtime.
 */
export const WorkspaceRuntimeEvents = {
  BeforeInitialize: 'runtime.beforeInitialize',
  AfterInitialize: 'runtime.afterInitialize',

  BeforeStart: 'runtime.beforeStart',
  AfterStart: 'runtime.afterStart',

  BeforeStop: 'runtime.beforeStop',
  AfterStop: 'runtime.afterStop',

  BeforeReset: 'runtime.beforeReset',
  AfterReset: 'runtime.afterReset',

  Failed: 'runtime.failed',
} as const;

/**
 * Nome válido de evento do Workspace Runtime.
 */
export type WorkspaceRuntimeEvent =
  (typeof WorkspaceRuntimeEvents)[keyof typeof WorkspaceRuntimeEvents];