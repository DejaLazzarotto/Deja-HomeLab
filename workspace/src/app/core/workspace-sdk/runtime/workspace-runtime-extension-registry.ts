import {
  WorkspaceOwnerId,
} from '../contracts/workspace-contracts';
import {
  WorkspaceRuntimeExtension,
  WorkspaceRuntimeExtensionId,
  WorkspaceRuntimeExtensionPointId,
} from './workspace-runtime-extension-point';

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
 * Responsabilidades:
 * - registrar extensões;
 * - impedir identificadores duplicados;
 * - permitir consulta por ponto de extensão;
 * - manter ordenação determinística;
 * - preservar independência de Angular.
 */
export class WorkspaceRuntimeExtensionRegistry {
  private readonly extensions = new Map<
    WorkspaceRuntimeExtensionId,
    WorkspaceRuntimeExtension
  >();

  register(extension: WorkspaceRuntimeExtension): void {
    if (this.extensions.has(extension.id)) {
      throw new WorkspaceRuntimeExtensionDuplicateError(extension.id);
    }

    this.extensions.set(extension.id, extension);
  }

  registerMany(extensions: readonly WorkspaceRuntimeExtension[]): void {
    for (const extension of extensions) {
      this.register(extension);
    }
  }

  replace(extension: WorkspaceRuntimeExtension): void {
    this.extensions.set(extension.id, extension);
  }

  unregister(extensionId: WorkspaceRuntimeExtensionId): boolean {
    return this.extensions.delete(extensionId);
  }

  unregisterByOwner(owner: WorkspaceOwnerId): number {
    const extensionIds = this.list()
      .filter((extension) => extension.owner === owner)
      .map((extension) => extension.id);

    for (const extensionId of extensionIds) {
      this.extensions.delete(extensionId);
    }

    return extensionIds.length;
  }

  clear(): void {
    this.extensions.clear();
  }

  has(extensionId: WorkspaceRuntimeExtensionId): boolean {
    return this.extensions.has(extensionId);
  }

  get(
    extensionId: WorkspaceRuntimeExtensionId,
  ): WorkspaceRuntimeExtension | undefined {
    return this.extensions.get(extensionId);
  }

  require(extensionId: WorkspaceRuntimeExtensionId): WorkspaceRuntimeExtension {
    const extension = this.get(extensionId);

    if (!extension) {
      throw new WorkspaceRuntimeExtensionNotFoundError(extensionId);
    }

    return extension;
  }

  list(): readonly WorkspaceRuntimeExtension[] {
    return this.sort([...this.extensions.values()]);
  }

  listByExtensionPoint(
    extensionPoint: WorkspaceRuntimeExtensionPointId,
  ): readonly WorkspaceRuntimeExtension[] {
    return this.sort(
      [...this.extensions.values()].filter(
        (extension) =>
          extension.extensionPoint === extensionPoint &&
          (extension.enabled ?? true),
      ),
    );
  }

  count(extensionPoint?: WorkspaceRuntimeExtensionPointId): number {
    if (extensionPoint === undefined) {
      return this.extensions.size;
    }

    return this.listByExtensionPoint(extensionPoint).length;
  }

  private sort(
    extensions: WorkspaceRuntimeExtension[],
  ): readonly WorkspaceRuntimeExtension[] {
    return extensions.sort((left, right) => {
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
