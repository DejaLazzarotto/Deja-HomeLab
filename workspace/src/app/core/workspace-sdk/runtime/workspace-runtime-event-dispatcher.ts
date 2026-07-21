import {
  WorkspaceRuntimeEvent,
} from './workspace-runtime-events';

/**
 * Contexto emitido pelos eventos do Workspace Runtime.
 */
export interface WorkspaceRuntimeEventContext {
  readonly event: WorkspaceRuntimeEvent;
  readonly timestamp: Date;
  readonly data?: Readonly<Record<string, unknown>>;
}

/**
 * Listener de eventos do Workspace Runtime.
 */
export type WorkspaceRuntimeEventListener = (
  context: WorkspaceRuntimeEventContext,
) => void | Promise<void>;

/**
 * Dispatcher oficial de eventos do Workspace Runtime.
 *
 * Responsabilidades:
 * - registrar listeners;
 * - remover listeners;
 * - emitir eventos de forma determinística;
 * - preservar a ordem de registro;
 * - suportar listeners síncronos e assíncronos.
 */
export class WorkspaceRuntimeEventDispatcher {
  private readonly listeners = new Map<
    WorkspaceRuntimeEvent,
    WorkspaceRuntimeEventListener[]
  >();

  on(
    event: WorkspaceRuntimeEvent,
    listener: WorkspaceRuntimeEventListener,
  ): () => void {
    const eventListeners = this.listeners.get(event) ?? [];

    eventListeners.push(listener);
    this.listeners.set(event, eventListeners);

    return () => {
      this.off(event, listener);
    };
  }

  off(
    event: WorkspaceRuntimeEvent,
    listener: WorkspaceRuntimeEventListener,
  ): boolean {
    const eventListeners = this.listeners.get(event);

    if (!eventListeners) {
      return false;
    }

    const listenerIndex = eventListeners.indexOf(listener);

    if (listenerIndex < 0) {
      return false;
    }

    eventListeners.splice(listenerIndex, 1);

    if (eventListeners.length === 0) {
      this.listeners.delete(event);
    }

    return true;
  }

  async emit(
    event: WorkspaceRuntimeEvent,
    data?: Readonly<Record<string, unknown>>,
  ): Promise<void> {
    const eventListeners = [
      ...(this.listeners.get(event) ?? []),
    ];

    const context: WorkspaceRuntimeEventContext = {
      event,
      timestamp: new Date(),
      data,
    };

    for (const listener of eventListeners) {
      await listener(context);
    }
  }

  listenerCount(event: WorkspaceRuntimeEvent): number {
    return this.listeners.get(event)?.length ?? 0;
  }

  clear(event?: WorkspaceRuntimeEvent): void {
    if (event) {
      this.listeners.delete(event);
      return;
    }

    this.listeners.clear();
  }
}