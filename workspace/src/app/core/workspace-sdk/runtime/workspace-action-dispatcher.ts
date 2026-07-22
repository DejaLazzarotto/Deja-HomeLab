import {
  WorkspaceAction,
  WorkspaceActionContext,
  WorkspaceActionExecution,
  WorkspaceActionId,
  WorkspaceActionResult,
} from './workspace-action';

import {
  WorkspaceActionRegistry,
} from './workspace-action-registry';

import {
  WorkspaceCommandDispatcher,
} from './workspace-command-dispatcher';

import {
  WorkspaceCommandResult,
} from './workspace-command';

/**
 * Erro lançado quando uma Action está desabilitada.
 */
export class WorkspaceActionDisabledError extends Error {
  constructor(readonly actionId: WorkspaceActionId) {
    super(`Workspace action is disabled: ${actionId}`);
    this.name = 'WorkspaceActionDisabledError';
  }
}

/**
 * Erro lançado quando uma Action não pode ser executada.
 */
export class WorkspaceActionCannotExecuteError extends Error {
  constructor(readonly actionId: WorkspaceActionId) {
    super(`Workspace action cannot execute: ${actionId}`);
    this.name = 'WorkspaceActionCannotExecuteError';
  }
}

/**
 * Erro lançado quando ocorre falha durante a execução.
 */
export class WorkspaceActionExecutionError extends Error {
  constructor(
    readonly actionId: WorkspaceActionId,
    readonly executionError: unknown,
  ) {
    super(`Workspace action execution failed: ${actionId}`);
    this.name = 'WorkspaceActionExecutionError';
  }
}

/**
 * Dispatcher oficial de Workspace Actions.
 *
 * Responsabilidades:
 * - localizar Actions;
 * - validar disponibilidade;
 * - construir contexto;
 * - executar Action Handler;
 * - encaminhar para Workspace Commands;
 * - normalizar resultados.
 */
export class WorkspaceActionDispatcher {
  constructor(
    private readonly registry: WorkspaceActionRegistry,
    private readonly commandDispatcher: WorkspaceCommandDispatcher,
  ) {}

  /**
   * Verifica se uma Action pode ser executada.
   */
  async canExecute<TPayload = unknown>(
    execution: WorkspaceActionExecution<TPayload>,
  ): Promise<boolean> {
    const action = this.registry.get(execution.actionId);

    if (action.enabled === false) {
      return false;
    }

    const context = this.createContext(action, execution);

    if (
      action.canExecute
      && !(await action.canExecute(context))
    ) {
      return false;
    }

    if (action.commandId) {
      return this.commandDispatcher.canExecute({
        commandId: action.commandId,
        payload: execution.payload,
        source: 'action',
        metadata: execution.metadata,
      });
    }

    return Boolean(action.execute);
  }

  /**
   * Executa uma Workspace Action.
   */
  async dispatch<
    TPayload = unknown,
    TResult = unknown,
  >(
    execution: WorkspaceActionExecution<TPayload>,
  ): Promise<WorkspaceActionResult<TResult>> {
    const action = this.registry.get(execution.actionId);

    if (action.enabled === false) {
      throw new WorkspaceActionDisabledError(action.id);
    }

    const context = this.createContext(action, execution);

    if (
      action.canExecute
      && !(await action.canExecute(context))
    ) {
      throw new WorkspaceActionCannotExecuteError(action.id);
    }

    try {
      if (action.commandId) {
        const result =
          await this.commandDispatcher.dispatch<
            TPayload,
            TResult
          >({
            commandId: action.commandId,
            payload: execution.payload,
            source: 'action',
            metadata: execution.metadata,
          });

        return this.fromCommandResult(result);
      }

      if (!action.execute) {
        throw new WorkspaceActionExecutionError(
          action.id,
          new Error('Action has neither commandId nor execute handler.'),
        );
      }

      const result = await action.execute(context);

      return this.normalizeResult<TResult>(result);
    } catch (error) {
      if (
        error instanceof WorkspaceActionDisabledError
        || error instanceof WorkspaceActionCannotExecuteError
        || error instanceof WorkspaceActionExecutionError
      ) {
        throw error;
      }

      throw new WorkspaceActionExecutionError(
        action.id,
        error,
      );
    }
  }

  /**
   * Executa diretamente uma Action pelo identificador.
   */
  async dispatchById<
    TPayload = unknown,
    TResult = unknown,
  >(
    actionId: WorkspaceActionId,
    payload?: TPayload,
  ): Promise<WorkspaceActionResult<TResult>> {
    return this.dispatch<TPayload, TResult>({
      actionId,
      payload,
      source: 'runtime',
    });
  }

  /**
   * Constrói o contexto oficial.
   */
  private createContext<TPayload>(
    action: WorkspaceAction<TPayload>,
    execution: WorkspaceActionExecution<TPayload>,
  ): WorkspaceActionContext<TPayload> {
    return {
      actionId: action.id,
      ownerId: action.ownerId,
      source: execution.source ?? 'unknown',
      payload: execution.payload as TPayload,
      requestedAt: new Date(),
      metadata: execution.metadata,
    };
  }

  /**
   * Converte resultados de Commands em resultados de Actions.
   */
  private fromCommandResult<TResult>(
    result: WorkspaceCommandResult<TResult>,
  ): WorkspaceActionResult<TResult> {
    return {
      success: result.success,
      value: result.value,
      message: result.message,
      error: result.error,
      completedAt: result.completedAt,
    };
  }

  /**
   * Normaliza retornos simples.
   */
  private normalizeResult<TResult>(
    result: unknown,
  ): WorkspaceActionResult<TResult> {
    if (this.isWorkspaceActionResult<TResult>(result)) {
      return result;
    }

    return {
      success: true,
      value: result as TResult,
      completedAt: new Date(),
    };
  }

  /**
   * Verifica se o retorno já segue o contrato oficial.
   */
  private isWorkspaceActionResult<TResult>(
    result: unknown,
  ): result is WorkspaceActionResult<TResult> {
    if (
      typeof result !== 'object'
      || result === null
    ) {
      return false;
    }

    return (
      'success' in result
      && typeof result.success === 'boolean'
      && 'completedAt' in result
      && result.completedAt instanceof Date
    );
  }
}
