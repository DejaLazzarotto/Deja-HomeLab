/*
 * Deja Workspace UI SDK
 *
 * Workspace Navigation Dispatcher
 *
 * Dispatcher institucional responsável pela coordenação da
 * navegação entre Workspace Dashboards.
 */

import {
  WorkspaceNavigation,
  WorkspaceNavigationId,
} from './workspace-navigation';

import {
  WorkspaceNavigationRegistry,
} from './workspace-navigation-registry';

import {
  WorkspaceDashboardResolver,
} from './workspace-dashboard-resolver';

import {
  WorkspaceLayoutController,
} from './workspace-layout-controller';

import {
  WorkspaceLayoutManager,
} from './workspace-layout-manager';

import {
  WorkspaceResolvedDashboard,
} from './workspace-resolved-dashboard';

/**
 * Erro lançado quando um item de navegação está desabilitado.
 */
export class WorkspaceNavigationDisabledError extends Error {

  constructor(
    readonly navigationId: WorkspaceNavigationId,
  ) {

    super(
      `Workspace navigation is disabled: ${navigationId}`,
    );

    this.name = 'WorkspaceNavigationDisabledError';

  }

}

/**
 * Erro lançado quando a infraestrutura de Layout necessária
 * para a navegação não está disponível.
 */
export class WorkspaceNavigationLayoutUnavailableError extends Error {

  constructor() {

    super(
      'Workspace layout infrastructure is unavailable.',
    );

    this.name =
      'WorkspaceNavigationLayoutUnavailableError';

  }

}

/**
 * Erro lançado quando uma navegação não pode ser concluída.
 */
export class WorkspaceNavigationDispatchError extends Error {

  constructor(
    readonly navigationId: WorkspaceNavigationId,
    readonly dispatchError: unknown,
  ) {

    super(
      `Workspace navigation failed: ${navigationId}`,
    );

    this.name = 'WorkspaceNavigationDispatchError';

  }

}

/**
 * Resultado institucional de uma navegação.
 */
export interface WorkspaceNavigationResult {

  /**
   * Item de navegação utilizado.
   */
  readonly navigation: WorkspaceNavigation;

  /**
   * Dashboard resolvido e aberto.
   */
  readonly dashboard: WorkspaceResolvedDashboard;

  /**
   * Instante em que a navegação foi concluída.
   */
  readonly completedAt: Date;

}

/**
 * Dispatcher institucional de Workspace Navigation.
 *
 * Responsabilidades:
 *
 * - localizar itens de navegação registrados;
 * - validar o estado de habilitação;
 * - resolver o Dashboard associado;
 * - encerrar a sessão de Layout anterior;
 * - abrir uma nova sessão institucional;
 * - manter a referência da navegação ativa;
 * - permanecer independente de Angular.
 */
export class WorkspaceNavigationDispatcher {

  private activeController?: WorkspaceLayoutController;

  private activeNavigation?: WorkspaceNavigation;

  constructor(
    private readonly registry: WorkspaceNavigationRegistry,
    private readonly dashboardResolver: WorkspaceDashboardResolver,
    private readonly layoutManager?: WorkspaceLayoutManager,
  ) {}

  /**
   * Retorna o item de navegação atualmente ativo.
   */
  current(): WorkspaceNavigation | undefined {

    return this.activeNavigation;

  }

  /**
   * Retorna o identificador da navegação atualmente ativa.
   */
  currentId(): WorkspaceNavigationId | undefined {

    return this.activeNavigation?.id;

  }

  /**
   * Verifica se determinado item está ativo.
   */
  isActive(
    navigationId: WorkspaceNavigationId,
  ): boolean {

    return this.activeNavigation?.id === navigationId;

  }

  /**
   * Executa uma navegação institucional.
   */
  async dispatch(
    navigationId: WorkspaceNavigationId,
  ): Promise<WorkspaceNavigationResult> {

    const navigation =
      this.registry.get(navigationId);

    if (navigation.enabled === false) {

      throw new WorkspaceNavigationDisabledError(
        navigation.id,
      );

    }

    if (!this.layoutManager) {

      throw new WorkspaceNavigationLayoutUnavailableError();

    }

    try {

      const dashboard =
        await this.dashboardResolver.resolve(
          navigation.dashboardId,
        );

      await this.closeActiveController();

      const controller =
        await this.layoutManager.open(dashboard);

      this.activeController = controller;
      this.activeNavigation = navigation;

      return {
        navigation,
        dashboard:
          controller.dashboard ?? dashboard,
        completedAt: new Date(),
      };

    } catch (error) {

      if (
        error instanceof WorkspaceNavigationDisabledError
        || error instanceof WorkspaceNavigationLayoutUnavailableError
        || error instanceof WorkspaceNavigationDispatchError
      ) {

        throw error;

      }

      throw new WorkspaceNavigationDispatchError(
        navigation.id,
        error,
      );

    }

  }

  /**
   * Encerra a navegação ativa.
   */
  async clear(): Promise<void> {

    await this.closeActiveController();

    this.activeNavigation = undefined;

  }

  /**
   * Encerra o Controller atualmente associado à navegação.
   */
  private async closeActiveController(): Promise<void> {

    if (!this.activeController) {

      return;

    }

    if (this.layoutManager) {

      await this.layoutManager.close(
        this.activeController,
      );

    }

    this.activeController = undefined;

  }

}