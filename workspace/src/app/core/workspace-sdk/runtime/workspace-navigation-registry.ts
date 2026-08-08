/*
 * Deja Workspace UI SDK
 *
 * Workspace Navigation Registry
 *
 * Registry oficial responsável pelo gerenciamento dos itens
 * institucionais de navegação do Workspace.
 */

import {
  WorkspaceOwnerId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceNavigation,
  WorkspaceNavigationId,
} from './workspace-navigation';

/**
 * Erro lançado quando um item de navegação duplicado é registrado.
 */
export class WorkspaceNavigationDuplicateError extends Error {

  constructor(
    readonly navigationId: WorkspaceNavigationId,
  ) {

    super(
      `Workspace navigation already registered: ${navigationId}`,
    );

    this.name = 'WorkspaceNavigationDuplicateError';

  }

}

/**
 * Erro lançado quando um item de navegação não existe.
 */
export class WorkspaceNavigationNotFoundError extends Error {

  constructor(
    readonly navigationId: WorkspaceNavigationId,
  ) {

    super(
      `Workspace navigation not found: ${navigationId}`,
    );

    this.name = 'WorkspaceNavigationNotFoundError';

  }

}

/**
 * Registry institucional de Workspace Navigation.
 *
 * Responsabilidades:
 * - registrar itens de navegação;
 * - impedir identificadores duplicados;
 * - consultar itens por identificador;
 * - consultar itens por proprietário;
 * - expor itens habilitados;
 * - remover itens;
 * - remover itens por proprietário;
 * - expor snapshots imutáveis.
 */
export class WorkspaceNavigationRegistry {

  private readonly navigations =
    new Map<WorkspaceNavigationId, WorkspaceNavigation>();

  /**
   * Registra um item de navegação.
   */
  register(
    navigation: WorkspaceNavigation,
  ): void {

    if (this.navigations.has(navigation.id)) {

      throw new WorkspaceNavigationDuplicateError(
        navigation.id,
      );

    }

    this.navigations.set(
      navigation.id,
      navigation,
    );

  }

  /**
   * Registra múltiplos itens de navegação.
   */
  registerAll(
    navigations: readonly WorkspaceNavigation[],
  ): void {

    for (const navigation of navigations) {

      this.register(navigation);

    }

  }

  /**
   * Retorna um item pelo identificador.
   */
  get(
    navigationId: WorkspaceNavigationId,
  ): WorkspaceNavigation {

    const navigation =
      this.navigations.get(navigationId);

    if (!navigation) {

      throw new WorkspaceNavigationNotFoundError(
        navigationId,
      );

    }

    return navigation;

  }

  /**
   * Retorna um item quando ele existe.
   */
  find(
    navigationId: WorkspaceNavigationId,
  ): WorkspaceNavigation | undefined {

    return this.navigations.get(navigationId);

  }

  /**
   * Verifica se um item está registrado.
   */
  has(
    navigationId: WorkspaceNavigationId,
  ): boolean {

    return this.navigations.has(navigationId);

  }

  /**
   * Retorna todos os itens registrados.
   */
  list(): readonly WorkspaceNavigation[] {

    return Object.freeze(
      [...this.navigations.values()]
        .sort(
          (left, right) =>
            (left.order ?? 0) - (right.order ?? 0),
        ),
    );

  }

  /**
   * Retorna os itens habilitados.
   */
  listEnabled(): readonly WorkspaceNavigation[] {

    return Object.freeze(
      this.list().filter(
        navigation => navigation.enabled !== false,
      ),
    );

  }

  /**
   * Retorna os itens habilitados e visíveis
   * na navegação principal do Workspace.
   */
  listVisible(): readonly WorkspaceNavigation[] {
    return Object.freeze(
      this.listEnabled().filter(
        navigation => navigation.visible !== false,
      ),
    );
  }

  /**
   * Retorna os itens pertencentes a um proprietário.
   */
  listByOwner(
    ownerId: WorkspaceOwnerId,
  ): readonly WorkspaceNavigation[] {

    return Object.freeze(
      this.list().filter(
        navigation => navigation.ownerId === ownerId,
      ),
    );

  }

  /**
   * Remove um item pelo identificador.
   */
  unregister(
    navigationId: WorkspaceNavigationId,
  ): WorkspaceNavigation {

    const navigation =
      this.get(navigationId);

    this.navigations.delete(navigationId);

    return navigation;

  }

  /**
   * Remove os itens pertencentes a um proprietário.
   */
  unregisterByOwner(
    ownerId: WorkspaceOwnerId,
  ): readonly WorkspaceNavigation[] {

    const removedNavigations: WorkspaceNavigation[] = [];

    for (
      const [navigationId, navigation]
      of this.navigations.entries()
    ) {

      if (navigation.ownerId !== ownerId) {

        continue;

      }

      this.navigations.delete(navigationId);
      removedNavigations.push(navigation);

    }

    return Object.freeze(removedNavigations);

  }

  /**
   * Remove todos os itens registrados.
   */
  clear(): void {

    this.navigations.clear();

  }

  /**
   * Retorna a quantidade de itens registrados.
   */
  get size(): number {

    return this.navigations.size;

  }

}