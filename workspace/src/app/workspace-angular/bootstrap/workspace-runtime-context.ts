/*
 * Deja Workspace Angular Integration
 *
 * Workspace Runtime Context
 *
 * Define o contexto oficial utilizado durante a inicialização
 * do Workspace Runtime na aplicação Angular.
 */

import {
  isDevMode,
} from '@angular/core';

import {
  WorkspaceRuntimeContext,
} from '../../core/workspace-sdk/models/workspace-models';

/**
 * Cria o contexto oficial do Workspace Runtime.
 */
export function createWorkspaceRuntimeContext(): WorkspaceRuntimeContext {

  return {
    applicationId: 'deja-workspace',
    environment: isDevMode()
      ? 'development'
      : 'production',
    metadata: {
      platform: 'angular',
    },
  };

}