/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Event Builders
 *
 * Funções auxiliares responsáveis pela criação padronizada
 * dos eventos institucionais de Layout.
 */

import {
  WorkspaceLayoutMutationOperation,
  WorkspaceLayoutMutationResult,
} from './workspace-layout-mutation';

import {
  WorkspaceLayoutMutatedEvent,
  WorkspaceLayoutRedoExecutedEvent,
  WorkspaceLayoutRestoredEvent,
  WorkspaceLayoutSessionClosedEvent,
  WorkspaceLayoutSessionOpenedEvent,
  WorkspaceLayoutUndoExecutedEvent,
} from './workspace-layout-events';

import {
  WorkspaceResolvedDashboard,
} from './workspace-resolved-dashboard';

/**
 * Cria um timestamp institucional para eventos de Layout.
 *
 * Permite que múltiplos eventos relacionados compartilhem a
 * mesma referência temporal quando necessário.
 */
export function createWorkspaceLayoutEventTimestamp(): Date {

  return new Date();

}

/**
 * Cria um SessionOpenedEvent.
 */
export function createWorkspaceLayoutSessionOpenedEvent(
  dashboard: WorkspaceResolvedDashboard,
): WorkspaceLayoutSessionOpenedEvent {

  return {

    type: 'session-opened',

    timestamp: createWorkspaceLayoutEventTimestamp(),

    dashboard,

  };

}

/**
 * Cria um SessionClosedEvent.
 */
export function createWorkspaceLayoutSessionClosedEvent(
  dashboard: WorkspaceResolvedDashboard,
): WorkspaceLayoutSessionClosedEvent {

  return {

    type: 'session-closed',

    timestamp: createWorkspaceLayoutEventTimestamp(),

    dashboard,

  };

}

/**
 * Cria um LayoutRestoredEvent.
 */
export function createWorkspaceLayoutRestoredEvent(
  dashboard: WorkspaceResolvedDashboard,
): WorkspaceLayoutRestoredEvent {

  return {

    type: 'layout-restored',

    timestamp: createWorkspaceLayoutEventTimestamp(),

    dashboard,

  };

}

/**
 * Cria um LayoutMutatedEvent.
 */
export function createWorkspaceLayoutMutatedEvent(
  mutation: WorkspaceLayoutMutationOperation,
  result: WorkspaceLayoutMutationResult,
  dashboard: WorkspaceResolvedDashboard,
): WorkspaceLayoutMutatedEvent {

  return {

    type: 'layout-mutated',

    timestamp: createWorkspaceLayoutEventTimestamp(),

    mutation,

    result,

    dashboard,

  };

}

/**
 * Cria um UndoExecutedEvent.
 */
export function createWorkspaceLayoutUndoExecutedEvent(
  dashboard: WorkspaceResolvedDashboard,
): WorkspaceLayoutUndoExecutedEvent {

  return {

    type: 'undo-executed',

    timestamp: createWorkspaceLayoutEventTimestamp(),

    dashboard,

  };

}

/**
 * Cria um RedoExecutedEvent.
 */
export function createWorkspaceLayoutRedoExecutedEvent(
  dashboard: WorkspaceResolvedDashboard,
): WorkspaceLayoutRedoExecutedEvent {

  return {

    type: 'redo-executed',

    timestamp: createWorkspaceLayoutEventTimestamp(),

    dashboard,

  };

}
