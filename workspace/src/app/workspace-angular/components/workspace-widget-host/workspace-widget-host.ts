/*
 * Deja Workspace Angular Integration
 *
 * Workspace Widget Host Component
 *
 * Componente responsável pela resolução institucional e
 * hospedagem de um único Workspace Widget.
 */

import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  ComponentRef,
  Input,
  OnChanges,
  OnDestroy,
  SimpleChanges,
  Type,
  ViewChild,
} from '@angular/core';

import {
  WorkspaceRuntime,
} from '../../../core/workspace-sdk/runtime/workspace-runtime';

import {
  WorkspaceWidget,
  WorkspaceWidgetInstance,
} from '../../../core/workspace-sdk/runtime/workspace-widget';

import {
  WorkspaceRenderHostDirective,
} from '../../rendering/workspace-render-host.directive';

/**
 * Host responsável pela resolução e criação dinâmica
 * de uma instância de Workspace Widget.
 */
@Component({
  selector: 'deja-workspace-widget-host',
  standalone: true,
  imports: [
    WorkspaceRenderHostDirective,
  ],
  template: `
    <section class="workspace-widget-host">
      <ng-container dejaWorkspaceRenderHost />
    </section>
  `,
  styles: `
    :host {
      display: block;
      width: 100%;
      height: 100%;
    }

    .workspace-widget-host {
      display: block;
      width: 100%;
      height: 100%;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceWidgetHostComponent
  implements AfterViewInit, OnChanges, OnDestroy {

  /**
   * Runtime oficial do Workspace.
   */
  @Input({
    required: true,
  })
  runtime!: WorkspaceRuntime;

  /**
   * Instância do Widget pertencente ao Dashboard.
   */
  @Input({
    required: true,
  })
  widgetInstance!: WorkspaceWidgetInstance;

  /**
   * Host Angular utilizado para criação dinâmica
   * do componente associado ao Widget.
   */
  @ViewChild(
    WorkspaceRenderHostDirective,
    {
      static: true,
    },
  )
  private renderHost!: WorkspaceRenderHostDirective;

  /**
   * Referência do componente Angular atualmente renderizado.
   */
  private widgetComponentRef?: ComponentRef<unknown>;

  /**
   * Indica que o host Angular já foi inicializado.
   */
  private viewInitialized = false;

  /**
   * Inicializa a renderização após a criação da View.
   */
  ngAfterViewInit(): void {

    this.viewInitialized = true;
    this.renderWidget();

  }

  /**
   * Recria o componente quando a instância ou o Runtime mudarem.
   */
  ngOnChanges(
    changes: SimpleChanges,
  ): void {

    if (
      !this.viewInitialized
      || (
        !changes['runtime']
        && !changes['widgetInstance']
      )
    ) {
      return;
    }

    this.renderWidget();

  }

  /**
   * Libera o componente Angular associado ao Widget.
   */
  ngOnDestroy(): void {

    this.disposeWidget();

  }

  /**
   * Resolve e renderiza o Widget.
   */
  private renderWidget(): void {

    this.disposeWidget();

    if (
      !this.runtime
      || !this.widgetInstance
      || this.widgetInstance.enabled === false
    ) {
      return;
    }

    const widget = this.runtime.requireWidget(
      this.widgetInstance.widgetId,
    );

    if (widget.enabled === false) {
      return;
    }

    const componentType = this.resolveComponentType(widget);

    this.widgetComponentRef =
      this.renderHost.viewContainerRef.createComponent(
        componentType,
        {
          environmentInjector:
            this.renderHost.environmentInjector,
        },
      );

    this.widgetComponentRef.setInput(
      'widgetInstance',
      this.widgetInstance,
    );

  }

  /**
   * Valida e retorna o componente Angular registrado
   * na definição institucional do Widget.
   */
  private resolveComponentType(
    widget: WorkspaceWidget,
  ): Type<unknown> {

    if (typeof widget.component !== 'function') {
      throw new Error(
        `Workspace widget "${widget.id}" does not define a valid Angular component.`,
      );
    }

    return widget.component as Type<unknown>;

  }

  /**
   * Destrói o componente Angular atualmente renderizado.
   */
  private disposeWidget(): void {

    if (this.widgetComponentRef) {
      this.widgetComponentRef.destroy();
      this.widgetComponentRef = undefined;
    }

    this.renderHost?.viewContainerRef.clear();

  }

}