/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Hook
 *
 * Contrato institucional responsável pela definição de Hooks
 * utilizados na interceptação do ciclo de vida das operações
 * de Workspace Layout.
 */

/**
 * Representa uma função institucional de Workspace Layout Hook.
 *
 * Um Hook pode executar operações síncronas ou assíncronas antes
 * ou depois de uma operação de Layout.
 *
 * O contexto recebido é definido pelo ponto específico do ciclo
 * de vida ao qual o Hook está associado.
 */
export type WorkspaceLayoutHook<TContext = void> = (
  context: TContext,
) => void | Promise<void>;
