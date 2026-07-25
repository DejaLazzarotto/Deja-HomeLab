/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Events
 *
 * Contratos institucionais dos eventos emitidos durante
 * o ciclo de vida das operações de edição de Layout.
 */

import {
  WorkspaceLayoutMutationOperation,
  WorkspaceLayoutMutationResult,
} from './workspace-layout-mutation';

import {
  WorkspaceResolvedDashboard,
} from './workspace-resolved-dashboard';

/**
 * Identificadores institucionais dos eventos de Layout.
 */
export type WorkspaceLayoutEventType =
  | 'session-opened'
  | 'session-closed'
  | 'layout-restored'
  | 'layout-mutated'
  | 'undo-executed'
  | 'redo-executed';

/**
 * Contrato base de todos os eventos institucionais de Layout.
 */
export interface WorkspaceLayoutEvent {

  /**
   * Tipo institucional do evento.
   */
  readonly type: WorkspaceLayoutEventType;

  /**
   * Data e hora em que o evento foi emitido.
   */
  readonly timestamp: Date;

}

/**
 * Evento emitido após a abertura de uma sessão de Layout.
 */
export interface WorkspaceLayoutSessionOpenedEvent
  extends WorkspaceLayoutEvent {

  readonly type: 'session-opened';

  /**
   * Dashboard mantido pela sessão aberta.
   */
  readonly dashboard: WorkspaceResolvedDashboard;

}

/**
 * Evento emitido após o encerramento de uma sessão de Layout.
 */
export interface WorkspaceLayoutSessionClosedEvent
  extends WorkspaceLayoutEvent {

  readonly type: 'session-closed';

  /**
   * Último Dashboard mantido pela sessão encerrada.
   */
  readonly dashboard: WorkspaceResolvedDashboard;

}

/**
 * Evento emitido após a restauração do Layout persistido.
 */
export interface WorkspaceLayoutRestoredEvent
  extends WorkspaceLayoutEvent {

  readonly type: 'layout-restored';

  /**
   * Dashboard resultante da restauração.
   */
  readonly dashboard: WorkspaceResolvedDashboard;

}

/**
 * Evento emitido após a aplicação de uma mutação estrutural.
 */
export interface WorkspaceLayoutMutatedEvent
  extends WorkspaceLayoutEvent {

  readonly type: 'layout-mutated';

  /**
   * Operação de mutação solicitada.
   */
  readonly mutation: WorkspaceLayoutMutationOperation;

  /**
   * Resultado institucional da mutação.
   */
  readonly result: WorkspaceLayoutMutationResult;

  /**
   * Dashboard corrente após a mutação.
   */
  readonly dashboard: WorkspaceResolvedDashboard;

}

/**
 * Evento emitido após a execução bem-sucedida de Undo.
 */
export interface WorkspaceLayoutUndoExecutedEvent
  extends WorkspaceLayoutEvent {

  readonly type: 'undo-executed';

  /**
   * Dashboard corrente após o Undo.
   */
  readonly dashboard: WorkspaceResolvedDashboard;

}

/**
 * Evento emitido após a execução bem-sucedida de Redo.
 */
export interface WorkspaceLayoutRedoExecutedEvent
  extends WorkspaceLayoutEvent {

  readonly type: 'redo-executed';

  /**
   * Dashboard corrente após o Redo.
   */
  readonly dashboard: WorkspaceResolvedDashboard;

}

/**
 * União institucional de todos os eventos de Layout.
 */
export type WorkspaceLayoutEvents =
  | WorkspaceLayoutSessionOpenedEvent
  | WorkspaceLayoutSessionClosedEvent
  | WorkspaceLayoutRestoredEvent
  | WorkspaceLayoutMutatedEvent
  | WorkspaceLayoutUndoExecutedEvent
  | WorkspaceLayoutRedoExecutedEvent;

/**
 * Listener institucional de eventos de Layout.
 */
/**
 * Listener institucional de eventos de Layout.
 */
export interface WorkspaceLayoutEventListener {

  (
    event: WorkspaceLayoutEvents,
  ): void;

}

/**
 * Assinatura institucional utilizada para cancelamento
 * de inscrições em eventos.
 */
export type WorkspaceLayoutEventSubscription = () => void;

/**
 * Registry institucional de listeners de Layout.
 *
 * Utilizado por componentes que desejam expor ou compartilhar
 * coleções de listeners sem depender diretamente da implementação
 * do Event Dispatcher.
 */
export interface WorkspaceLayoutEventRegistry {

  /**
   * Registra um listener.
   */
  addListener(
    listener: WorkspaceLayoutEventListener,
  ): void;

  /**
   * Remove um listener.
   */
  removeListener(
    listener: WorkspaceLayoutEventListener,
  ): boolean;

  /**
   * Verifica se um listener está registrado.
   */
  hasListener(
    listener: WorkspaceLayoutEventListener,
  ): boolean;

  /**
   * Remove todos os listeners.
   */
  removeAllListeners(): void;

  /**
   * Retorna uma função de cancelamento da inscrição.
   */
  subscribe(
    listener: WorkspaceLayoutEventListener,
  ): WorkspaceLayoutEventSubscription;

}