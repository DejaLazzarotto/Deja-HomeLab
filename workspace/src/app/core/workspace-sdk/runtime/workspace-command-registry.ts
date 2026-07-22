import {
  WorkspaceOwnerId,
} from '../contracts/workspace-contracts';
import {
  WorkspaceCommand,
  WorkspaceCommandId,
} from './workspace-command';

/**
 * Erro lançado quando um comando duplicado é registrado.
 */
export class WorkspaceCommandDuplicateError extends Error {
  constructor(readonly commandId: WorkspaceCommandId) {
    super(`Workspace command already registered: ${commandId}`);
    this.name = 'WorkspaceCommandDuplicateError';
  }
}

/**
 * Erro lançado quando um comando solicitado não existe.
 */
export class WorkspaceCommandNotFoundError extends Error {
  constructor(readonly commandId: WorkspaceCommandId) {
    super(`Workspace command not found: ${commandId}`);
    this.name = 'WorkspaceCommandNotFoundError';
  }
}

/**
 * Registry oficial de Workspace Commands.
 *
 * Responsabilidades:
 * - registrar comandos;
 * - impedir identificadores duplicados;
 * - consultar comandos por identificador;
 * - consultar comandos por proprietário;
 * - remover comandos;
 * - remover comandos por proprietário;
 * - expor snapshots imutáveis.
 */
export class WorkspaceCommandRegistry {
  private readonly commands = new Map<
    WorkspaceCommandId,
    WorkspaceCommand
  >();

  /**
   * Registra um Workspace Command.
   */
  register(command: WorkspaceCommand): void {
    if (this.commands.has(command.id)) {
      throw new WorkspaceCommandDuplicateError(command.id);
    }

    this.commands.set(command.id, command);
  }

  /**
   * Registra múltiplos Workspace Commands.
   */
  registerAll(commands: readonly WorkspaceCommand[]): void {
    for (const command of commands) {
      this.register(command);
    }
  }

  /**
   * Retorna um comando pelo identificador.
   */
  get(commandId: WorkspaceCommandId): WorkspaceCommand {
    const command = this.commands.get(commandId);

    if (!command) {
      throw new WorkspaceCommandNotFoundError(commandId);
    }

    return command;
  }

  /**
   * Retorna um comando quando ele existe.
   */
  find(commandId: WorkspaceCommandId): WorkspaceCommand | undefined {
    return this.commands.get(commandId);
  }

  /**
   * Verifica se um comando está registrado.
   */
  has(commandId: WorkspaceCommandId): boolean {
    return this.commands.has(commandId);
  }

  /**
   * Retorna todos os comandos registrados.
   */
  list(): readonly WorkspaceCommand[] {
    return Object.freeze([...this.commands.values()]);
  }

  /**
   * Retorna os comandos pertencentes a um proprietário.
   */
  listByOwner(ownerId: WorkspaceOwnerId): readonly WorkspaceCommand[] {
    return Object.freeze(
      [...this.commands.values()].filter(
        (command) => command.ownerId === ownerId,
      ),
    );
  }

  /**
   * Remove um comando pelo identificador.
   */
  unregister(commandId: WorkspaceCommandId): WorkspaceCommand {
    const command = this.get(commandId);

    this.commands.delete(commandId);

    return command;
  }

  /**
   * Remove todos os comandos pertencentes a um proprietário.
   */
  unregisterByOwner(ownerId: WorkspaceOwnerId): readonly WorkspaceCommand[] {
    const removedCommands: WorkspaceCommand[] = [];

    for (const [commandId, command] of this.commands.entries()) {
      if (command.ownerId !== ownerId) {
        continue;
      }

      this.commands.delete(commandId);
      removedCommands.push(command);
    }

    return Object.freeze(removedCommands);
  }

  /**
   * Remove todos os comandos registrados.
   */
  clear(): void {
    this.commands.clear();
  }

  /**
   * Retorna a quantidade de comandos registrados.
   */
  get size(): number {
    return this.commands.size;
  }
}