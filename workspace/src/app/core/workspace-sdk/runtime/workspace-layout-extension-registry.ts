import {
  WorkspaceOwnerId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceLayoutExtension,
  WorkspaceLayoutExtensionId,
  WorkspaceLayoutExtensionPointId,
} from './workspace-layout-extension-point';

import {
  WorkspaceRuntimeRegistry,
  WorkspaceRuntimeRegistryDuplicateError,
} from './workspace-runtime-registry';

/**
 * Erro lançado quando uma extensão de Layout duplicada
 * é registrada.
 */
export class WorkspaceLayoutExtensionDuplicateError extends Error {

  constructor(
    readonly extensionId: WorkspaceLayoutExtensionId,
  ) {

    super(
      `Workspace layout extension already registered: ${extensionId}`,
    );

    this.name = 'WorkspaceLayoutExtensionDuplicateError';

  }

}

/**
 * Erro lançado quando uma extensão de Layout solicitada
 * não existe.
 */
export class WorkspaceLayoutExtensionNotFoundError extends Error {

  constructor(
    readonly extensionId: WorkspaceLayoutExtensionId,
  ) {

    super(
      `Workspace layout extension not found: ${extensionId}`,
    );

    this.name = 'WorkspaceLayoutExtensionNotFoundError';

  }

}

/**
 * Registry oficial de extensões do Workspace Layout.
 *
 * Utiliza WorkspaceRuntimeRegistry como infraestrutura
 * genérica de armazenamento, preservando uma API pública
 * específica para as Workspace Layout Extensions.
 *
 * Responsabilidades:
 *
 * - registrar extensões;
 * - impedir identificadores duplicados;
 * - permitir consulta por ponto de extensão;
 * - remover extensões por proprietário;
 * - manter ordenação determinística por prioridade;
 * - preservar independência de Angular, Runtime e persistência.
 */
export class WorkspaceLayoutExtensionRegistry {

  private readonly registry = new WorkspaceRuntimeRegistry<
    WorkspaceLayoutExtension,
    WorkspaceLayoutExtensionId
  >();

  /**
   * Registra uma extensão de Layout.
   *
   * @throws WorkspaceLayoutExtensionDuplicateError
   * quando o identificador já estiver registrado.
   */
  register(
    extension: WorkspaceLayoutExtension,
  ): void {

    try {

      this.registry.register(extension);

    } catch (error) {

      if (error instanceof WorkspaceRuntimeRegistryDuplicateError) {

        throw new WorkspaceLayoutExtensionDuplicateError(
          extension.id,
        );

      }

      throw error;

    }

  }

  /**
   * Registra múltiplas extensões na ordem recebida.
   */
  registerMany(
    extensions: readonly WorkspaceLayoutExtension[],
  ): void {

    for (const extension of extensions) {

      this.register(extension);

    }

  }

  /**
   * Substitui uma extensão existente ou registra
   * uma nova extensão.
   */
  replace(
    extension: WorkspaceLayoutExtension,
  ): void {

    this.registry.tryUnregister(extension.id);

    this.registry.register(extension);

  }

  /**
   * Remove uma extensão.
   *
   * @returns true quando a extensão existia e foi removida;
   * false quando não estava registrada.
   */
  unregister(
    extensionId: WorkspaceLayoutExtensionId,
  ): boolean {

    return this.registry.tryUnregister(extensionId) !== undefined;

  }

  /**
   * Remove todas as extensões pertencentes ao owner informado.
   *
   * @returns quantidade de extensões removidas.
   */
  unregisterByOwner(
    owner: WorkspaceOwnerId,
  ): number {

    const extensionIds = this.registry
      .values()
      .filter(
        (extension) => extension.owner === owner,
      )
      .map(
        (extension) => extension.id,
      );

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
  has(
    extensionId: WorkspaceLayoutExtensionId,
  ): boolean {

    return this.registry.has(extensionId);

  }

  /**
   * Retorna uma extensão ou undefined.
   */
  get(
    extensionId: WorkspaceLayoutExtensionId,
  ): WorkspaceLayoutExtension | undefined {

    return this.registry.find(extensionId);

  }

  /**
   * Retorna uma extensão obrigatória.
   *
   * @throws WorkspaceLayoutExtensionNotFoundError
   * quando a extensão não existir.
   */
  require(
    extensionId: WorkspaceLayoutExtensionId,
  ): WorkspaceLayoutExtension {

    const extension = this.get(extensionId);

    if (!extension) {

      throw new WorkspaceLayoutExtensionNotFoundError(
        extensionId,
      );

    }

    return extension;

  }

  /**
   * Retorna todas as extensões em ordem determinística.
   */
  list(): readonly WorkspaceLayoutExtension[] {

    return this.sort([
      ...this.registry.values(),
    ]);

  }

  /**
   * Retorna as extensões habilitadas associadas
   * a um ponto de extensão.
   */
  listByExtensionPoint(
    extensionPoint: WorkspaceLayoutExtensionPointId,
  ): readonly WorkspaceLayoutExtension[] {

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
   * Retorna a quantidade total de extensões ou
   * a quantidade associada a um ponto de extensão.
   */
  count(
    extensionPoint?: WorkspaceLayoutExtensionPointId,
  ): number {

    if (extensionPoint === undefined) {

      return this.registry.size;

    }

    return this.listByExtensionPoint(extensionPoint).length;

  }

  /**
   * Ordena extensões por prioridade e, em caso de empate,
   * preserva a ordem original de registro fornecida
   * pelo registry institucional.
   */
  private sort(
    extensions: readonly WorkspaceLayoutExtension[],
  ): readonly WorkspaceLayoutExtension[] {

    return extensions
      .map(
        (extension, registrationIndex) => ({
          extension,
          registrationIndex,
        }),
      )
      .sort((left, right) => {

        const priorityDifference =
          (
            left.extension.priority ??
            Number.MAX_SAFE_INTEGER
          ) -
          (
            right.extension.priority ??
            Number.MAX_SAFE_INTEGER
          );

        if (priorityDifference !== 0) {

          return priorityDifference;

        }

        return (
          left.registrationIndex -
          right.registrationIndex
        );

      })
      .map(
        ({ extension }) => extension,
      );

  }

}