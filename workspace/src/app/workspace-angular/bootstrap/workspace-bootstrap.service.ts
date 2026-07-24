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

/**
 * Serviço oficial responsável pelo bootstrap
 * do Workspace Runtime.
 */
@Injectable({
  providedIn: 'root',
})
export class WorkspaceBootstrapService {

  private readonly runtime = new WorkspaceRuntime();

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