import {
  WorkspaceOwnerId,
} from '../contracts/workspace-contracts';
import {
  WorkspaceRuntimeExtension,
  WorkspaceRuntimeExtensionId,
  WorkspaceRuntimeExtensionPointId,
} from './workspace-runtime-extension-point';
import {
  WorkspaceRuntimeRegistry,
  WorkspaceRuntimeRegistryDuplicateError,
} from './workspace-runtime-registry';

/**
 * Erro lançado quando uma extensão duplicada é registrada.
 */
export class WorkspaceRuntimeExtensionDuplicateError extends Error {
  constructor(readonly extensionId: WorkspaceRuntimeExtensionId) {
    super(`Workspace runtime extension already registered: ${extensionId}`);
    this.name = 'WorkspaceRuntimeExtensionDuplicateError';
  }
}

/**
 * Erro lançado quando uma extensão solicitada não existe.
 */
export class WorkspaceRuntimeExtensionNotFoundError extends Error {
  constructor(readonly extensionId: WorkspaceRuntimeExtensionId) {
    super(`Workspace runtime extension not found: ${extensionId}`);
    this.name = 'WorkspaceRuntimeExtensionNotFoundError';
  }
}

/**
 * Registry oficial de extensões do Workspace Runtime.
 *
 * Utiliza WorkspaceRuntimeRegistry como infraestrutura genérica,
 * preservando a API pública específica das Runtime Extensions.
 *
 * Responsabilidades:
 * - registrar extensões;
 * - impedir identificadores duplicados;
 * - permitir consulta por ponto de extensão;
 * - manter ordenação determinística;
 * - preservar independência de Angular.
 */
export class WorkspaceRuntimeExtensionRegistry {
  private readonly registry = new WorkspaceRuntimeRegistry<
    WorkspaceRuntimeExtension,
    WorkspaceRuntimeExtensionId
  >();

  /**
   * Registra uma extensão.
   *
   * @throws WorkspaceRuntimeExtensionDuplicateError
   * quando o identificador já estiver registrado.
   */
  register(extension: WorkspaceRuntimeExtension): void {
    try {
      this.registry.register(extension);
    } catch (error) {
      if (error instanceof WorkspaceRuntimeRegistryDuplicateError) {
        throw new WorkspaceRuntimeExtensionDuplicateError(extension.id);
      }

      throw error;
    }
  }

  /**
   * Registra múltiplas extensões na ordem recebida.
   */
  registerMany(extensions: readonly WorkspaceRuntimeExtension[]): void {
    for (const extension of extensions) {
      this.register(extension);
    }
  }

  /**
   * Substitui uma extensão existente ou registra uma nova extensão.
   */
  replace(extension: WorkspaceRuntimeExtension): void {
    this.registry.tryUnregister(extension.id);
    this.registry.register(extension);
  }

  /**
   * Remove uma extensão.
   *
   * @returns true quando a extensão existia e foi removida;
   * false quando não estava registrada.
   */
  unregister(extensionId: WorkspaceRuntimeExtensionId): boolean {
    return this.registry.tryUnregister(extensionId) !== undefined;
  }

  /**
   * Remove todas as extensões pertencentes ao owner informado.
   *
   * @returns quantidade de extensões removidas.
   */
  unregisterByOwner(owner: WorkspaceOwnerId): number {
    const extensionIds = this.registry
      .values()
      .filter((extension) => extension.owner === owner)
      .map((extension) => extension.id);

    for (const extensionId of extensionIds) {
      this.registry.tryUnregister(extensionId);
    }

    return extensionIds.length;
  }

  /**
   * Remove todas as extensões registradas.
   */
  clear(): void {
    this.registry.clear();
  }

  /**
   * Verifica se uma extensão está registrada.
   */
  has(extensionId: WorkspaceRuntimeExtensionId): boolean {
    return this.registry.has(extensionId);
  }

  /**
   * Retorna uma extensão ou undefined.
   */
  get(
    extensionId: WorkspaceRuntimeExtensionId,
  ): WorkspaceRuntimeExtension | undefined {
    return this.registry.find(extensionId);
  }

  /**
   * Retorna uma extensão obrigatória.
   *
   * @throws WorkspaceRuntimeExtensionNotFoundError
   * quando a extensão não existir.
   */
  require(extensionId: WorkspaceRuntimeExtensionId): WorkspaceRuntimeExtension {
    const extension = this.get(extensionId);

    if (!extension) {
      throw new WorkspaceRuntimeExtensionNotFoundError(extensionId);
    }

    return extension;
  }

  /**
   * Retorna todas as extensões em ordem determinística.
   */
  list(): readonly WorkspaceRuntimeExtension[] {
    return this.sort([...this.registry.values()]);
  }

  /**
   * Retorna as extensões habilitadas de um ponto de extensão.
   */
  listByExtensionPoint(
    extensionPoint: WorkspaceRuntimeExtensionPointId,
  ): readonly WorkspaceRuntimeExtension[] {
    return this.sort(
      this.registry
        .values()
        .filter(
          (extension) =>
            extension.extensionPoint === extensionPoint &&
            (extension.enabled ?? true),
        ),
    );
  }

  /**
   * Retorna a quantidade total de extensões ou a quantidade
   * associada a um ponto de extensão.
   */
  count(extensionPoint?: WorkspaceRuntimeExtensionPointId): number {
    if (extensionPoint === undefined) {
      return this.registry.size;
    }

    return this.listByExtensionPoint(extensionPoint).length;
  }

  /**
   * Ordena extensões por prioridade e, em caso de empate,
   * pelo identificador.
   */
  private sort(
    extensions: readonly WorkspaceRuntimeExtension[],
  ): readonly WorkspaceRuntimeExtension[] {
    return [...extensions].sort((left, right) => {
      const priorityDifference =
        (left.priority ?? Number.MAX_SAFE_INTEGER) -
        (right.priority ?? Number.MAX_SAFE_INTEGER);

      if (priorityDifference !== 0) {
        return priorityDifference;
      }

      return left.id.localeCompare(right.id);
    });
  }
}
