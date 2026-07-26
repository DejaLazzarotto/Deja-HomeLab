/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Hooks
 *
 * Contratos institucionais responsáveis pelos Hooks do ciclo
 * de vida das operações de Workspace Layout.
 */

import {
  WorkspaceLayoutHook,
} from './workspace-layout-hook';

import {
  WorkspaceLayoutMutationResult,
} from './workspace-layout-mutation';

import {
  WorkspaceLayoutSession,
} from './workspace-layout-session';

/**
 * Conjunto institucional de Hooks utilizados durante o ciclo
 * de vida das operações de Layout.
 */
export interface WorkspaceLayoutHooks {

  /**
   * Executado antes da abertura de uma sessão.
   */
  readonly beforeSessionOpen?: WorkspaceLayoutHook;

  /**
   * Executado após a abertura de uma sessão.
   */
  readonly afterSessionOpen?: WorkspaceLayoutHook<WorkspaceLayoutSession>;

  /**
   * Executado antes do encerramento de uma sessão.
   */
  readonly beforeSessionClose?: WorkspaceLayoutHook<WorkspaceLayoutSession>;

  /**
   * Executado após o encerramento de uma sessão.
   */
  readonly afterSessionClose?: WorkspaceLayoutHook;

  /**
   * Executado antes da restauração do Layout.
   */
  readonly beforeRestore?: WorkspaceLayoutHook<WorkspaceLayoutSession>;

  /**
   * Executado após a restauração do Layout.
   */
  readonly afterRestore?: WorkspaceLayoutHook<WorkspaceLayoutSession>;

  /**
   * Executado antes da aplicação de uma mutação.
   */
  readonly beforeMutation?: WorkspaceLayoutHook<WorkspaceLayoutSession>;

  /**
   * Executado após a aplicação de uma mutação.
   */
  readonly afterMutation?: WorkspaceLayoutHook<WorkspaceLayoutMutationResult>;

  /**
   * Executado antes de uma operação de Undo.
   */
  readonly beforeUndo?: WorkspaceLayoutHook<WorkspaceLayoutSession>;

  /**
   * Executado após uma operação de Undo concluída.
   */
  readonly afterUndo?: WorkspaceLayoutHook<WorkspaceLayoutSession>;

  /**
   * Executado antes de uma operação de Redo.
   */
  readonly beforeRedo?: WorkspaceLayoutHook<WorkspaceLayoutSession>;

  /**
   * Executado após uma operação de Redo concluída.
   */
  readonly afterRedo?: WorkspaceLayoutHook<WorkspaceLayoutSession>;

}