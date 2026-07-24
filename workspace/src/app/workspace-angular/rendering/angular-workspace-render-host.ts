/*
 * Deja Workspace Angular Integration
 *
 * Angular Workspace Render Host
 *
 * Contrato da integração Angular responsável por encapsular
 * os recursos necessários para a criação dinâmica de componentes.
 */

import {
  EnvironmentInjector,
  ViewContainerRef,
} from '@angular/core';

/**
 * Host oficial de renderização da integração Angular.
 *
 * Este contrato pertence exclusivamente à camada Angular e não
 * introduz qualquer dependência Angular no Workspace SDK.
 */
export interface AngularWorkspaceRenderHost {

  /**
   * Container Angular onde os componentes serão renderizados.
   */
  readonly viewContainerRef: ViewContainerRef;

  /**
   * Injector utilizado na criação dinâmica dos componentes.
   */
  readonly environmentInjector: EnvironmentInjector;

}