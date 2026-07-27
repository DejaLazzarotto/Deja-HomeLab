/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Factory
 *
 * Infraestrutura institucional responsável pela composição
 * completa do subsistema de Layout do Workspace.
 */

import {
  WorkspaceLayoutEventDispatcher,
} from './workspace-layout-event-dispatcher';

import {
  WorkspaceLayoutExtensionDispatcher,
} from './workspace-layout-extension-dispatcher';

import {
  WorkspaceLayoutHookDispatcher,
} from './workspace-layout-hook-dispatcher';

import {
  WorkspaceLayoutManager,
} from './workspace-layout-manager';

import {
  WorkspaceLayoutObservability,
} from './workspace-layout-observability';

import {
  WorkspaceLayoutPersistence,
} from './workspace-layout-persistence';

import {
  WorkspaceLayoutServices,
} from './workspace-layout-services';

/**
 * Factory institucional responsável pela composição da
 * infraestrutura de Layout.
 *
 * Esta infraestrutura concentra toda a criação dos
 * componentes necessários ao funcionamento do subsistema,
 * mantendo o Workspace Runtime completamente desacoplado
 * dos detalhes de implementação.
 *
 * A Factory permanece independente:
 *
 * - do Angular;
 * - da tecnologia de renderização;
 * - do Workspace Runtime;
 * - do Dashboard Resolver;
 * - da infraestrutura de edição.
 */
export class WorkspaceLayoutFactory {

  constructor(
    private readonly persistence: WorkspaceLayoutPersistence,
    private readonly events: WorkspaceLayoutEventDispatcher,
    private readonly hooks: WorkspaceLayoutHookDispatcher,
    private readonly extensions: WorkspaceLayoutExtensionDispatcher,
    private readonly observability: WorkspaceLayoutObservability,
  ) {}

  /**
   * Cria uma nova infraestrutura institucional de Layout.
   */
  create(): WorkspaceLayoutManager {

    const services = new WorkspaceLayoutServices(
      this.persistence,
      this.events,
      this.hooks,
      this.extensions,
      this.observability,
    );

    return new WorkspaceLayoutManager(
      services,
    );

  }

}