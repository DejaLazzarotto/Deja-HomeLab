import {
  WorkspaceOwnerId,
  WorkspaceRegistryQuery,
  WorkspaceResource,
  WorkspaceResourceId,
} from '../contracts/workspace-contracts';

/**
 * Erro lançado quando um recurso duplicado é registrado.
 */
export class WorkspaceRegistryDuplicateError extends Error {
  constructor(readonly resourceId: WorkspaceResourceId) {
    super(`Workspace resource already registered: ${resourceId}`);
    this.name = 'WorkspaceRegistryDuplicateError';
  }
}

/**
 * Erro lançado quando um recurso solicitado não existe.
 */
export class WorkspaceRegistryResourceNotFoundError extends Error {
  constructor(readonly resourceId: WorkspaceResourceId) {
    super(`Workspace resource not found: ${resourceId}`);
    this.name = 'WorkspaceRegistryResourceNotFoundError';
  }
}

/**
 * Registry genérico, determinístico e independente de Angular.
 */
export class WorkspaceRegistry<
  TResource extends WorkspaceResource<TId>,
  TId extends WorkspaceResourceId = WorkspaceResourceId,
> {
  private readonly resources = new Map<TId, TResource>();

  register(resource: TResource): void {
    if (this.resources.has(resource.id)) {
      throw new WorkspaceRegistryDuplicateError(resource.id);
    }

    this.resources.set(resource.id, resource);
  }

  registerMany(resources: readonly TResource[]): void {
    for (const resource of resources) {
      this.register(resource);
    }
  }

  replace(resource: TResource): void {
    this.resources.set(resource.id, resource);
  }

  unregister(resourceId: TId): boolean {
    return this.resources.delete(resourceId);
  }

  clear(): void {
    this.resources.clear();
  }

  has(resourceId: TId): boolean {
    return this.resources.has(resourceId);
  }

  get(resourceId: TId): TResource | undefined {
    return this.resources.get(resourceId);
  }

  require(resourceId: TId): TResource {
    const resource = this.get(resourceId);

    if (!resource) {
      throw new WorkspaceRegistryResourceNotFoundError(resourceId);
    }

    return resource;
  }

  list(query?: WorkspaceRegistryQuery): readonly TResource[] {
    return this.sort(
      [...this.resources.values()].filter((resource) =>
        this.matchesQuery(resource, query),
      ),
    );
  }

  listByOwner(owner: WorkspaceOwnerId): readonly TResource[] {
    return this.list({ owner });
  }

  count(query?: WorkspaceRegistryQuery): number {
    return this.list(query).length;
  }

  private matchesQuery(
    resource: TResource,
    query?: WorkspaceRegistryQuery,
  ): boolean {
    if (!query) {
      return true;
    }

    if (query.owner !== undefined && resource.owner !== query.owner) {
      return false;
    }

    if (
      query.enabled !== undefined &&
      (resource.enabled ?? true) !== query.enabled
    ) {
      return false;
    }

    if (query.tags?.length) {
      const resourceTags = this.getResourceTags(resource);

      if (!query.tags.every((tag) => resourceTags.includes(tag))) {
        return false;
      }
    }

    return true;
  }

  private getResourceTags(resource: TResource): readonly string[] {
    const candidate = resource as TResource & {
      readonly tags?: readonly string[];
    };

    return candidate.tags ?? [];
  }

  private sort(resources: TResource[]): readonly TResource[] {
    return resources.sort((left, right) => {
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
