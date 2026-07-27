/*
 * Deja Workspace UI SDK
 *
 * Workspace Editing Manager
 *
 * Fachada pública institucional responsável pela exposição
 * das operações de edição do Workspace.
 */

import {
  WorkspaceDashboardRegionId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceLayoutController,
} from './workspace-layout-controller';

import {
  WorkspaceLayoutManager,
} from './workspace-layout-manager';

import {
  WorkspaceLayoutMutationBuilder,
} from './workspace-layout-mutation-builder';

import {
  WorkspaceLayoutMutationOperation,
  WorkspaceLayoutMutationResult,
} from './workspace-layout-mutation';

import {
  WorkspaceLayoutSession,
} from './workspace-layout-session';

import {
  WorkspaceResolvedDashboard,
} from './workspace-resolved-dashboard';

import {
  WorkspaceGridPosition,
  WorkspaceWidgetInstance,
} from './workspace-widget';

/**
 * Fachada pública oficial da Workspace Editing API.
 *
 * Responsável por:
 *
 * - abrir sessões de edição;
 * - encerrar sessões de edição;
 * - expor operações institucionais de edição;
 * - ocultar completamente o WorkspaceLayoutController
 *   das aplicações consumidoras.
 */
export class WorkspaceEditingManager {

  private readonly mutationBuilder =
    new WorkspaceLayoutMutationBuilder();

  private activeController?: WorkspaceLayoutController;

  constructor(
    private readonly layoutManager: WorkspaceLayoutManager,
  ) {}

  /**
   * Abre uma nova sessão de edição.
   */
  async open(
    dashboard: WorkspaceResolvedDashboard,
  ): Promise<void> {

    this.activeController = await this.layoutManager.open(
      dashboard,
    );

  }

  /**
   * Encerra a sessão ativa.
   */
  async close(): Promise<void> {

    if (!this.activeController) {
      return;
    }

    await this.layoutManager.close(
      this.activeController,
    );

    this.activeController = undefined;

  }

  /**
   * Indica se existe uma sessão ativa.
   */
  isEditing(): boolean {

    return this.activeController !== undefined;

  }

  /**
   * Retorna o Dashboard atualmente em edição.
   */
  dashboard(): WorkspaceResolvedDashboard | undefined {

    return this.activeController?.dashboard;

  }

  /**
   * Move uma instância de Widget.
   */
  async moveWidget(
    widgetInstanceId: string,
    position: WorkspaceGridPosition,
    regionId?: WorkspaceDashboardRegionId,
  ): Promise<WorkspaceLayoutMutationResult> {

    const mutation = this.mutationBuilder.moveWidget(
      widgetInstanceId,
      position,
      regionId,
    );

    return this.requireController().mutate(
      mutation,
    );

  }

  /**
   * Redimensiona uma instância de Widget.
   */
  async resizeWidget(
    widgetInstanceId: string,
    columnSpan?: number,
    rowSpan?: number,
  ): Promise<WorkspaceLayoutMutationResult> {

    const mutation = this.mutationBuilder.resizeWidget(
      widgetInstanceId,
      columnSpan,
      rowSpan,
    );

    return this.requireController().mutate(
      mutation,
    );

  }

  /**
   * Adiciona uma instância de Widget.
   */
  async addWidget(
    widget: WorkspaceWidgetInstance,
  ): Promise<WorkspaceLayoutMutationResult> {

    const mutation = this.mutationBuilder.addWidget(
      widget,
    );

    return this.requireController().mutate(
      mutation,
    );

  }

  /**
   * Restaura o Layout persistido.
   */
  async restore(): Promise<WorkspaceResolvedDashboard> {

    return this.requireController().restore();

  }

  /**
   * Executa Undo.
   */
  async undo(): Promise<boolean> {

    return this.requireController().undo();

  }

  /**
   * Executa Redo.
   */
  async redo(): Promise<boolean> {

    return this.requireController().redo();

  }

  /**
   * Aplica uma mutação estrutural ao Workspace atualmente
   * em edição.
   *
   * Mantido para compatibilidade durante a migração para
   * a API de alto nível.
   */
  async mutate(
    mutation: WorkspaceLayoutMutationOperation,
  ): Promise<WorkspaceLayoutMutationResult> {

    return this.requireController().mutate(
      mutation,
    );

  }

  /**
   * Retorna a sessão atualmente ativa.
   *
   * Mantido temporariamente para compatibilidade
   * durante a evolução da Workspace Editing API.
   */
  session(): WorkspaceLayoutSession | undefined {

    return (this.activeController as unknown as {
      activeSession?: WorkspaceLayoutSession;
    }).activeSession;

  }

  /**
   * Retorna o Controller ativo.
   */
  private requireController(): WorkspaceLayoutController {

    if (!this.activeController) {
      throw new Error(
        'No workspace editing session is active.',
      );
    }

    return this.activeController;

  }

}