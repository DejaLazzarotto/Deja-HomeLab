/*
 * Deja Workspace UI SDK
 *
 * Workspace Editing Factory
 *
 * Responsável pela composição institucional da
 * Workspace Editing API.
 */

import {
  WorkspaceEditingManager,
} from './workspace-editing-manager';

import {
  WorkspaceLayoutManager,
} from './workspace-layout-manager';

/**
 * Ponto único de composição da infraestrutura de edição.
 *
 * Esta infraestrutura permanece independente:
 *
 * - do Workspace Runtime;
 * - da camada de renderização;
 * - da persistência concreta;
 * - das aplicações consumidoras.
 *
 * Futuramente esta Factory será responsável por compor
 * toda a infraestrutura da Workspace Editing API,
 * incluindo Selection, Drag & Drop, Resize, Clipboard,
 * Alignment, Snap e demais serviços institucionais.
 */
export class WorkspaceEditingFactory {

  constructor(
    private readonly layoutManager: WorkspaceLayoutManager,
  ) {}

  /**
   * Cria uma nova instância da Workspace Editing API.
   */
  createManager(): WorkspaceEditingManager {

    return new WorkspaceEditingManager(
      this.layoutManager,
    );

  }

}