import {
  WorkspaceServiceId,
} from '../contracts/workspace-contracts';
import {
  WorkspaceServiceDefinition,
} from '../models/workspace-models';
import {
  WorkspaceServiceRegistry,
} from '../registries/workspace-registries';

/**
 * Erro lançado quando um serviço não está registrado.
 */
export class WorkspaceServiceNotFoundError extends Error {
  constructor(readonly serviceId: WorkspaceServiceId) {
    super(`Workspace service not found: ${serviceId}`);
    this.name = 'WorkspaceServiceNotFoundError';
  }
}

/**
 * Erro lançado quando a criação de um serviço falha.
 */
export class WorkspaceServiceCreationError extends Error {
  constructor(
    readonly serviceId: WorkspaceServiceId,
    override readonly cause: unknown,
  ) {
    super(`Workspace service creation failed: ${serviceId}`);
    this.name = 'WorkspaceServiceCreationError';
  }
}

/**
 * Container oficial de serviços do Workspace SDK.
 *
 * Responsabilidades:
 * - resolver definições registradas;
 * - criar instâncias sob demanda;
 * - manter cache singleton por serviço;
 * - preservar independência de Angular;
 * - permitir descarte determinístico.
 */
export class WorkspaceServices {
  private readonly instances = new Map<WorkspaceServiceId, unknown>();

  private readonly pendingInstances = new Map<
    WorkspaceServiceId,
    Promise<unknown>
  >();

  constructor(
    private readonly registry: WorkspaceServiceRegistry,
  ) {}

  has(serviceId: WorkspaceServiceId): boolean {
    return this.registry.has(serviceId);
  }

  isResolved(serviceId: WorkspaceServiceId): boolean {
    return this.instances.has(serviceId);
  }

  async resolve<TService>(
    serviceId: WorkspaceServiceId,
  ): Promise<TService> {
    const existingInstance = this.instances.get(serviceId);

    if (existingInstance !== undefined) {
      return existingInstance as TService;
    }

    const pendingInstance = this.pendingInstances.get(serviceId);

    if (pendingInstance) {
      return pendingInstance as Promise<TService>;
    }

    const definition = this.registry.get(serviceId);

    if (!definition) {
      throw new WorkspaceServiceNotFoundError(serviceId);
    }

    const creation = this.createInstance<TService>(definition);

    this.pendingInstances.set(serviceId, creation);

    try {
      const instance = await creation;

      this.instances.set(serviceId, instance);

      return instance;
    } finally {
      this.pendingInstances.delete(serviceId);
    }
  }

  get<TService>(
    serviceId: WorkspaceServiceId,
  ): TService | undefined {
    return this.instances.get(serviceId) as TService | undefined;
  }

  require<TService>(
    serviceId: WorkspaceServiceId,
  ): TService {
    const instance = this.get<TService>(serviceId);

    if (instance === undefined) {
      throw new WorkspaceServiceNotFoundError(serviceId);
    }

    return instance;
  }

  async dispose(serviceId: WorkspaceServiceId): Promise<boolean> {
    const instance = this.instances.get(serviceId);

    if (instance === undefined) {
      return false;
    }

    await this.disposeInstance(instance);

    this.instances.delete(serviceId);

    return true;
  }

  async disposeAll(): Promise<void> {
    const serviceIds = [...this.instances.keys()].reverse();

    for (const serviceId of serviceIds) {
      await this.dispose(serviceId);
    }
  }

  clear(): void {
    this.instances.clear();
    this.pendingInstances.clear();
  }

  listResolved(): readonly WorkspaceServiceId[] {
    return [...this.instances.keys()].sort((left, right) =>
      left.localeCompare(right),
    );
  }

  private async createInstance<TService>(
    definition: WorkspaceServiceDefinition,
  ): Promise<TService> {
    try {
      return (await definition.factory()) as TService;
    } catch (error) {
      throw new WorkspaceServiceCreationError(
        definition.id,
        error,
      );
    }
  }

  private async disposeInstance(instance: unknown): Promise<void> {
    if (
      typeof instance === 'object' &&
      instance !== null &&
      'dispose' in instance &&
      typeof instance.dispose === 'function'
    ) {
      await instance.dispose();
    }
  }
}
