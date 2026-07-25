/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Event Dispatcher
 *
 * Infraestrutura institucional responsável pela distribuição
 * dos eventos de Layout para consumidores externos.
 */

import {
  WorkspaceLayoutEventListener,
  WorkspaceLayoutEventRegistry,
  WorkspaceLayoutEvents,
  WorkspaceLayoutEventSubscription,
} from './workspace-layout-events';

/**
 * Dispatcher institucional de Workspace Layout Events.
 *
 * Permanece completamente independente:
 *
 * - do Workspace Runtime;
 * - do Workspace Layout Controller;
 * - do Workspace Layout Session;
 * - do mecanismo de persistência;
 * - da tecnologia de renderização;
 * - de Angular;
 * - de Electron.
 */
export class WorkspaceLayoutEventDispatcher
  implements WorkspaceLayoutEventRegistry {

  private readonly registeredListeners =
    new Set<WorkspaceLayoutEventListener>();

  /**
   * Quantidade de listeners registrados.
   */
  get size(): number {

    return this.registeredListeners.size;

  }

  /**
   * Indica se existem listeners registrados.
   */
  get hasListeners(): boolean {

    return this.size > 0;

  }

  /**
   * Registra um listener institucional.
   */
  addListener(
    listener: WorkspaceLayoutEventListener,
  ): void {

    this.registeredListeners.add(
      listener,
    );

  }

  /**
   * Registra um listener e retorna uma função institucional
   * para cancelamento da inscrição.
   */
  subscribe(
    listener: WorkspaceLayoutEventListener,
  ): WorkspaceLayoutEventSubscription {

    this.addListener(
      listener,
    );

    return this.removeListener.bind(
      this,
      listener,
    );

  }

  /**
   * Verifica se um listener está registrado.
   */
  hasListener(
    listener: WorkspaceLayoutEventListener,
  ): boolean {

    return this.registeredListeners.has(
      listener,
    );

  }

  /**
   * Remove um listener institucional.
   */
  removeListener(
    listener: WorkspaceLayoutEventListener,
  ): boolean {

    return this.registeredListeners.delete(
      listener,
    );

  }

  /**
   * Retorna uma representação somente leitura dos listeners
   * registrados, preservando a ordem de registro.
   */
  listeners(): readonly WorkspaceLayoutEventListener[] {

    return Array.from(
      this.registeredListeners,
    );

  }

  /**
   * Executa uma ação para cada listener registrado,
   * preservando a ordem de registro.
   */
  forEach(
    action: (
      listener: WorkspaceLayoutEventListener,
    ) => void,
  ): void {

    for (const listener of this.listeners()) {

      action(
        listener,
      );

    }

  }

  /**
   * Retorna a quantidade de listeners registrados que
   * satisfazem um predicado.
   */
  count(
    predicate: (
      listener: WorkspaceLayoutEventListener,
    ) => boolean,
  ): number {

    let total = 0;

    for (const listener of this.listeners()) {

      if (predicate(listener)) {

        total++;

      }

    }

    return total;

  }

  /**
   * Remove todos os listeners registrados.
   */
  removeAllListeners(): void {

    this.registeredListeners.clear();

  }

  /**
   * Publica um evento institucional para todos os listeners
   * registrados.
   *
   * Uma cópia da coleção é utilizada para impedir que alterações
   * realizadas durante a emissão afetem a iteração corrente.
   *
   * A ordem de registro dos listeners é preservada durante toda
   * a publicação.
   */
  dispatch(
    event: WorkspaceLayoutEvents,
  ): void {

    for (const listener of this.listeners()) {

      listener(
        event,
      );

    }

  }

}