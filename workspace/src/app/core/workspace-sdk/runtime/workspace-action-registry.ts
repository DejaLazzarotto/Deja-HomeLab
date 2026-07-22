import {
  WorkspaceOwnerId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceAction,
  WorkspaceActionId,
} from './workspace-action';

/**
 * Erro lançado quando uma Action duplicada é registrada.
 */
export class WorkspaceActionDuplicateError extends Error {
  constructor(readonly actionId: WorkspaceActionId) {
    super(`Workspace action already registered: ${actionId}`);
    this.name = 'WorkspaceActionDuplicateError';
  }
}

/**
 * Erro lançado quando uma Action solicitada não existe.
 */
export class WorkspaceActionNotFoundError extends Error {
  constructor(readonly actionId: WorkspaceActionId) {
    super(`Workspace action not found: ${actionId}`);
    this.name = 'WorkspaceActionNotFoundError';
  }
}

/**
 * Registry oficial de Workspace Actions.
 *
 * Responsabilidades:
 * - registrar Actions;
 * - impedir identificadores duplicados;
 * - consultar Actions por identificador;
 * - consultar Actions por proprietário;
 * - remover Actions;
 * - remover Actions por proprietário;
 * - expor snapshots imutáveis.
 */
export class WorkspaceActionRegistry {
  private readonly actions = new Map<
    WorkspaceActionId,
    WorkspaceAction
  >();

  /**
   * Registra uma Workspace Action.
   */
  register(action: WorkspaceAction): void {
    if (this.actions.has(action.id)) {
      throw new WorkspaceActionDuplicateError(action.id);
    }

    this.actions.set(action.id, action);
  }

  /**
   * Registra múltiplas Workspace Actions.
   */
  registerAll(
    actions: readonly WorkspaceAction[],
  ): void {
    for (const action of actions) {
      this.register(action);
    }
  }

  /**
   * Retorna uma Action pelo identificador.
   */
  get(
    actionId: WorkspaceActionId,
  ): WorkspaceAction {
    const action = this.actions.get(actionId);

    if (!action) {
      throw new WorkspaceActionNotFoundError(actionId);
    }

    return action;
  }

  /**
   * Retorna uma Action quando ela existe.
   */
  find(
    actionId: WorkspaceActionId,
  ): WorkspaceAction | undefined {
    return this.actions.get(actionId);
  }

  /**
   * Verifica se uma Action está registrada.
   */
  has(
    actionId: WorkspaceActionId,
  ): boolean {
    return this.actions.has(actionId);
  }

  /**
   * Retorna todas as Actions registradas.
   */
  list(): readonly WorkspaceAction[] {
    return Object.freeze([
      ...this.actions.values(),
    ]);
  }

  /**
   * Retorna todas as Actions pertencentes a um proprietário.
   */
  listByOwner(
    ownerId: WorkspaceOwnerId,
  ): readonly WorkspaceAction[] {
    return Object.freeze(
      [...this.actions.values()].filter(
        (action) => action.ownerId === ownerId,
      ),
    );
  }

  /**
   * Remove uma Action.
   */
  unregister(
    actionId: WorkspaceActionId,
  ): WorkspaceAction {
    const action = this.get(actionId);

    this.actions.delete(actionId);

    return action;
  }

  /**
   * Remove todas as Actions de um proprietário.
   */
  unregisterByOwner(
    ownerId: WorkspaceOwnerId,
  ): readonly WorkspaceAction[] {
    const removedActions: WorkspaceAction[] = [];

    for (const [actionId, action] of this.actions.entries()) {
      if (action.ownerId !== ownerId) {
        continue;
      }

      this.actions.delete(actionId);
      removedActions.push(action);
    }

    return Object.freeze(removedActions);
  }

  /**
   * Remove todas as Actions registradas.
   */
  clear(): void {
    this.actions.clear();
  }

  /**
   * Quantidade de Actions registradas.
   */
  get size(): number {
    return this.actions.size;
  }
}
