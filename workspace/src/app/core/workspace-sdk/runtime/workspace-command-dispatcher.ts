import {
  WorkspaceCommand,
  WorkspaceCommandContext,
  WorkspaceCommandExecution,
  WorkspaceCommandId,
  WorkspaceCommandResult,
} from './workspace-command';
import {
  WorkspaceCommandRegistry,
} from './workspace-command-registry';

/**
 * Erro lançado quando um comando está desabilitado.
 */
export class WorkspaceCommandDisabledError extends Error {
  constructor(readonly commandId: WorkspaceCommandId) {
    super(`Workspace command is disabled: ${commandId}`);
    this.name = 'WorkspaceCommandDisabledError';
  }
}

/**
 * Erro lançado quando um comando não pode ser executado
 * no contexto atual.
 */
export class WorkspaceCommandCannotExecuteError extends Error {
  constructor(readonly commandId: WorkspaceCommandId) {
    super(`Workspace command cannot execute: ${commandId}`);
    this.name = 'WorkspaceCommandCannotExecuteError';
  }
}

/**
 * Erro lançado quando a execução de um comando falha.
 */
export class WorkspaceCommandExecutionError extends Error {
  constructor(
    readonly commandId: WorkspaceCommandId,
    readonly executionError: unknown,
  ) {
    super(`Workspace command execution failed: ${commandId}`);
    this.name = 'WorkspaceCommandExecutionError';
  }
}

/**
 * Dispatcher oficial de Workspace Commands.
 *
 * Responsabilidades:
 * - localizar comandos registrados;
 * - construir o contexto oficial de execução;
 * - validar disponibilidade;
 * - executar handlers síncronos ou assíncronos;
 * - normalizar resultados;
 * - encapsular falhas de execução.
 */
export class WorkspaceCommandDispatcher {
  constructor(
    private readonly registry: WorkspaceCommandRegistry,
  ) {}

  /**
   * Verifica se um comando pode ser executado.
   */
  async canExecute<TPayload = unknown>(
    execution: WorkspaceCommandExecution<TPayload>,
  ): Promise<boolean> {
    const command = this.registry.get(execution.commandId);

    if (command.enabled === false) {
      return false;
    }

    if (!command.canExecute) {
      return true;
    }

    const context = this.createContext(command, execution);

    return command.canExecute(context);
  }

  /**
   * Executa um Workspace Command.
   */
  async dispatch<
    TPayload = unknown,
    TResult = unknown,
  >(
    execution: WorkspaceCommandExecution<TPayload>,
  ): Promise<WorkspaceCommandResult<TResult>> {
    const command = this.registry.get(execution.commandId);

    if (command.enabled === false) {
      throw new WorkspaceCommandDisabledError(command.id);
    }

    const context = this.createContext(command, execution);

    if (
      command.canExecute
      && !(await command.canExecute(context))
    ) {
      throw new WorkspaceCommandCannotExecuteError(command.id);
    }

    try {
      const result = await command.execute(context);

      return this.normalizeResult<TResult>(result);
    } catch (error) {
      if (
        error instanceof WorkspaceCommandDisabledError
        || error instanceof WorkspaceCommandCannotExecuteError
        || error instanceof WorkspaceCommandExecutionError
      ) {
        throw error;
      }

      throw new WorkspaceCommandExecutionError(
        command.id,
        error,
      );
    }
  }

  /**
   * Executa um comando diretamente pelo identificador.
   */
  async dispatchById<
    TPayload = unknown,
    TResult = unknown,
  >(
    commandId: WorkspaceCommandId,
    payload?: TPayload,
  ): Promise<WorkspaceCommandResult<TResult>> {
    return this.dispatch<TPayload, TResult>({
      commandId,
      payload,
      source: 'runtime',
    });
  }

  /**
   * Constrói o contexto oficial de execução.
   */
  private createContext<TPayload>(
    command: WorkspaceCommand<TPayload>,
    execution: WorkspaceCommandExecution<TPayload>,
  ): WorkspaceCommandContext<TPayload> {
    return {
      commandId: command.id,
      ownerId: command.ownerId,
      source: execution.source ?? 'unknown',
      payload: execution.payload as TPayload,
      requestedAt: new Date(),
      metadata: execution.metadata,
    };
  }

  /**
   * Normaliza valores simples e resultados estruturados.
   */
  private normalizeResult<TResult>(
    result: unknown,
  ): WorkspaceCommandResult<TResult> {
    if (this.isWorkspaceCommandResult<TResult>(result)) {
      return result;
    }

    return {
      success: true,
      value: result as TResult,
      completedAt: new Date(),
    };
  }

  /**
   * Verifica se o valor retornado já segue o contrato oficial.
   */
  private isWorkspaceCommandResult<TResult>(
    result: unknown,
  ): result is WorkspaceCommandResult<TResult> {
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