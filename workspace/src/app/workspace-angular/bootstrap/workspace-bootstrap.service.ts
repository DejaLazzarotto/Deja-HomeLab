/*
 * Deja Workspace Angular Integration
 *
 * Workspace Bootstrap Service
 *
 * Responsável pela criação e inicialização do
 * Workspace Runtime.
 */

import {
  Injectable,
} from '@angular/core';

import {
  WorkspaceRuntime,
} from '../../core/workspace-sdk/runtime/workspace-runtime';

import {
  AngularWorkspaceRendererProvider,
} from '../rendering/angular-workspace-renderer-provider';

import {
  WorkspaceComposition,
} from './workspace-composition';

/**
 * Serviço oficial responsável pelo bootstrap
 * do Workspace Runtime.
 */
@Injectable({
  providedIn: 'root',
})
export class WorkspaceBootstrapService {

  /**
   * Runtime oficial da plataforma.
   *
   * Sua composição é centralizada pelo
   * WorkspaceComposition.
   */
  private readonly runtime =
    WorkspaceComposition.create();

  constructor(
    private readonly rendererProvider: AngularWorkspaceRendererProvider,
  ) {}

  /**
   * Retorna a instância oficial do Runtime.
   */
  getRuntime(): WorkspaceRuntime {

    return this.runtime;

  }

  /**
   * Registra toda a infraestrutura Angular.
   */
  configure(): void {

    this.rendererProvider.register(
      this.runtime,
    );

  }

}