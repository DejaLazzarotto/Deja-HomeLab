/*
 * Deja Workspace Angular Integration
 *
 * Workspace Widget Component Cache
 *
 * Cache institucional responsável pelo gerenciamento das
 * referências Angular das instâncias de Widgets renderizadas.
 */

import {
  Injectable,
} from '@angular/core';

import {
  WorkspaceWidgetReferenceRegistry,
} from '../../core/workspace-sdk/runtime/workspace-widget-reference-registry';

import {
  WorkspaceWidgetInstance,
} from '../../core/workspace-sdk/runtime/workspace-widget';

import {
  WorkspaceWidgetComponentReference,
} from './workspace-widget-component-reference';

/**
 * Cache institucional das referências de componentes Angular
 * associados às instâncias de Widgets ativas do Workspace.
 *
 * Esta infraestrutura permanece independente:
 *
 * - do Layout Engine;
 * - das mutações de Layout;
 * - do Dashboard;
 * - do Grid;
 * - da API pública do Workspace SDK.
 *
 * Além de sua responsabilidade concreta na integração Angular,
 * esta infraestrutura implementa o contrato institucional de
 * localização de Widgets renderizados definido pelo Workspace SDK.
 */
@Injectable({
  providedIn: 'root',
})
export class WorkspaceWidgetComponentCache
  implements WorkspaceWidgetReferenceRegistry {

  private readonly references = new Map<
    WorkspaceWidgetInstance['id'],
    WorkspaceWidgetComponentReference
  >();

  /**
   * Registra ou substitui a referência associada a uma
   * instância de Widget.
   */
  set(
    reference: WorkspaceWidgetComponentReference,
  ): void {

    this.references.set(
      reference.widgetInstanceId,
      reference,
    );

  }

  /**
   * Retorna a referência associada à instância informada.
   */
  get(
    widgetInstanceId: WorkspaceWidgetInstance['id'],
  ): WorkspaceWidgetComponentReference | undefined {

    return this.references.get(
      widgetInstanceId,
    );

  }

  /**
   * Verifica se existe uma referência associada à instância.
   */
  has(
    widgetInstanceId: WorkspaceWidgetInstance['id'],
  ): boolean {

    return this.references.has(
      widgetInstanceId,
    );

  }

  /**
   * Remove a referência associada à instância informada.
   */
  delete(
    widgetInstanceId: WorkspaceWidgetInstance['id'],
  ): boolean {

    return this.references.delete(
      widgetInstanceId,
    );

  }

  /**
   * Remove todas as referências registradas.
   */
  clear(): void {

    this.references.clear();

  }

  /**
   * Retorna todas as referências atualmente registradas.
   */
  values(): readonly WorkspaceWidgetComponentReference[] {

    return [
      ...this.references.values(),
    ];

  }

  /**
   * Retorna a quantidade de instâncias atualmente registradas.
   */
  size(): number {

    return this.references.size;

  }

}