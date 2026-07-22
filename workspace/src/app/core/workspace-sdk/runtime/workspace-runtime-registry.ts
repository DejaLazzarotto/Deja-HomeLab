/**
 * Identificador aceito pelos registros internos do Workspace Runtime.
 */
export type WorkspaceRuntimeRegistryItemId = string;

/**
 * Contrato mínimo exigido para elementos armazenados em um
 * WorkspaceRuntimeRegistry.
 */
export interface WorkspaceRuntimeRegistryItem<
  TId extends WorkspaceRuntimeRegistryItemId =
    WorkspaceRuntimeRegistryItemId,
> {
  readonly id: TId;
}

/**
 * Erro lançado quando um elemento duplicado é registrado.
 */
export class WorkspaceRuntimeRegistryDuplicateError<
  TId extends WorkspaceRuntimeRegistryItemId =
    WorkspaceRuntimeRegistryItemId,
> extends Error {
  constructor(readonly itemId: TId) {
    super(`Workspace runtime registry item already registered: ${itemId}`);
    this.name = 'WorkspaceRuntimeRegistryDuplicateError';
  }
}

/**
 * Erro lançado quando um elemento solicitado não existe.
 */
export class WorkspaceRuntimeRegistryNotFoundError<
  TId extends WorkspaceRuntimeRegistryItemId =
    WorkspaceRuntimeRegistryItemId,
> extends Error {
  constructor(readonly itemId: TId) {
    super(`Workspace runtime registry item not found: ${itemId}`);
    this.name = 'WorkspaceRuntimeRegistryNotFoundError';
  }
}

/**
 * Registry genérico utilizado pelas infraestruturas internas do
 * Workspace Runtime.
 *
 * Responsabilidades:
 * - registrar elementos identificáveis;
 * - impedir identificadores duplicados;
 * - recuperar elementos por identificador;
 * - verificar a existência de elementos;
 * - remover registros;
 * - fornecer snapshots imutáveis;
 * - preservar a ordem de registro.
 */
export class WorkspaceRuntimeRegistry<
  TItem extends WorkspaceRuntimeRegistryItem<TId>,
  TId extends WorkspaceRuntimeRegistryItemId =
    WorkspaceRuntimeRegistryItemId,
> {
  private readonly items = new Map<TId, TItem>();

  /**
   * Registra um novo elemento.
   *
   * @throws WorkspaceRuntimeRegistryDuplicateError
   * quando o identificador já estiver registrado.
   */
  register(item: TItem): void {
    if (this.items.has(item.id)) {
      throw new WorkspaceRuntimeRegistryDuplicateError(item.id);
    }

    this.items.set(item.id, item);
  }

  /**
   * Registra um elemento quando ele ainda não existe.
   *
   * @returns true quando o elemento foi registrado;
   * false quando já existia.
   */
  tryRegister(item: TItem): boolean {
    if (this.items.has(item.id)) {
      return false;
    }

    this.items.set(item.id, item);

    return true;
  }

  /**
   * Retorna um elemento pelo identificador.
   *
   * @throws WorkspaceRuntimeRegistryNotFoundError
   * quando o elemento não existir.
   */
  get(itemId: TId): TItem {
    const item = this.items.get(itemId);

    if (!item) {
      throw new WorkspaceRuntimeRegistryNotFoundError(itemId);
    }

    return item;
  }

  /**
   * Retorna um elemento pelo identificador ou undefined.
   */
  find(itemId: TId): TItem | undefined {
    return this.items.get(itemId);
  }

  /**
   * Verifica se um identificador está registrado.
   */
  has(itemId: TId): boolean {
    return this.items.has(itemId);
  }

  /**
   * Remove um elemento registrado.
   *
   * @throws WorkspaceRuntimeRegistryNotFoundError
   * quando o elemento não existir.
   */
  unregister(itemId: TId): TItem {
    const item = this.get(itemId);

    this.items.delete(itemId);

    return item;
  }

  /**
   * Remove um elemento quando ele existir.
   *
   * @returns o elemento removido ou undefined.
   */
  tryUnregister(itemId: TId): TItem | undefined {
    const item = this.items.get(itemId);

    if (!item) {
      return undefined;
    }

    this.items.delete(itemId);

    return item;
  }

  /**
   * Retorna todos os elementos na ordem de registro.
   */
  values(): readonly TItem[] {
    return Object.freeze(Array.from(this.items.values()));
  }

  /**
   * Retorna todos os identificadores na ordem de registro.
   */
  ids(): readonly TId[] {
    return Object.freeze(Array.from(this.items.keys()));
  }

  /**
   * Retorna a quantidade de elementos registrados.
   */
  get size(): number {
    return this.items.size;
  }

  /**
   * Informa se o registry está vazio.
   */
  get isEmpty(): boolean {
    return this.items.size === 0;
  }

  /**
   * Remove todos os registros.
   */
  clear(): void {
    this.items.clear();
  }
}