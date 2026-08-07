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

import {
  WorkspaceWidgetComponentCache,
} from '../../rendering/workspace-widget-component-cache';

import {
  WorkspaceWidgetRenderController,
} from '../../rendering/workspace-widget-render-controller';

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
  templateUrl: './workspace-widget-host.html',
  styleUrl: './workspace-widget-host.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceWidgetHostComponent
implements
AfterViewInit,
OnChanges,
OnDestroy,
WorkspaceWidgetRenderController {

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
   * Identificador da instância atualmente registrada no cache.
   */
  private registeredWidgetInstanceId?:
    WorkspaceWidgetInstance['id'];

  /**
   * Indica que o host Angular já foi inicializado.
   */
  private viewInitialized = false;

  /**
   * Definição institucional do Widget atualmente renderizado.
   */
  protected resolvedWidget?: WorkspaceWidget;

  constructor(
    private readonly widgetComponentCache:
      WorkspaceWidgetComponentCache,
  ) {}

  /**
   * Retorna o título efetivo apresentado pelo Widget.
   *
   * O título específico da instância possui prioridade sobre
   * o título institucional definido pelo Widget.
   */
  protected get widgetTitle(): string {

    return (
      this.widgetInstance?.title
      ?? this.resolvedWidget?.title
      ?? ''
    );

  }

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
   * Executa a movimentação incremental do Widget.
   *
   * A atualização concreta da posição será implementada
   * durante a evolução do Widget Diff Engine.
   */
  move(): boolean {

    return false;

  }

  /**
   * Executa o redimensionamento incremental do Widget.
   *
   * A atualização concreta das dimensões será implementada
   * durante a evolução do Widget Diff Engine.
   */
  resize(): boolean {

    return false;

  }

  /**
   * Anexa o Widget à árvore Angular de renderização.
   *
   * Quando o host já está inicializado, a renderização pode
   * ser executada institucionalmente.
   */
  attach(): boolean {

    if (!this.viewInitialized) {
      return false;
    }

    this.renderWidget();

    return this.widgetComponentRef !== undefined;

  }

  /**
   * Destrói incrementalmente o Widget renderizado.
   */
  destroy(): boolean {

    this.disposeWidget();

    return true;

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

    this.resolvedWidget = widget;

    const componentType =
      this.resolveComponentType(widget);

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

    this.registerWidgetComponent();

  }

  /**
   * Registra esta instância viva no cache institucional.
   */
  private registerWidgetComponent(): void {

    this.registeredWidgetInstanceId =
      this.widgetInstance.id;

    this.widgetComponentCache.set({
      widgetInstanceId:
        this.registeredWidgetInstanceId,
      component:
        this,
      controller:
        this,
    });

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
   * Destrói o componente Angular atualmente renderizado
   * e remove sua referência do cache institucional.
   */
  private disposeWidget(): void {

    this.resolvedWidget = undefined;

    if (
      this.registeredWidgetInstanceId
      !== undefined
    ) {

      this.widgetComponentCache.delete(
        this.registeredWidgetInstanceId,
      );

      this.registeredWidgetInstanceId =
        undefined;

    }

    if (this.widgetComponentRef) {

      this.widgetComponentRef.destroy();

      this.widgetComponentRef =
        undefined;

    }

    this.renderHost?.viewContainerRef.clear();

  }

}