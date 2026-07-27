/*
 * Deja Workspace Angular Integration
 *
 * Workspace Dashboard Component
 *
 * Componente responsável pela representação visual institucional
 * de um Dashboard resolvido pelo Workspace Runtime.
 */

import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  Input,
  OnDestroy,
  OnInit,
} from '@angular/core';

import {
  WorkspaceDashboardState,
  WorkspaceDashboardStateUnsubscribe,
} from '../../../core/workspace-sdk/runtime/workspace-dashboard-state';

import {
  WorkspaceLayoutRegion,
} from '../../../core/workspace-sdk/runtime/workspace-layout-region';

import {
  WorkspaceResolvedDashboard,
} from '../../../core/workspace-sdk/runtime/workspace-resolved-dashboard';

import {
  WorkspaceRuntime,
} from '../../../core/workspace-sdk/runtime/workspace-runtime';

import {
  WorkspaceWidgetInstance,
} from '../../../core/workspace-sdk/runtime/workspace-widget';

import {
  WorkspaceGridContainerDirective,
} from '../../rendering/workspace-grid-container.directive';

import {
  WorkspaceGridItemDirective,
} from '../../rendering/workspace-grid-item.directive';

import {
  WorkspaceWidgetHostComponent,
} from '../workspace-widget-host/workspace-widget-host';

/**
 * Representação Angular de um Workspace Dashboard.
 */
@Component({
  selector: 'deja-workspace-dashboard',
  standalone: true,
  imports: [
    WorkspaceWidgetHostComponent,
    WorkspaceGridContainerDirective,
    WorkspaceGridItemDirective,
  ],
  template: `
    <section class="workspace-dashboard">

      <header class="workspace-dashboard__header">

        <h1 class="workspace-dashboard__title">
          {{ resolvedDashboard.dashboard.title }}
        </h1>

        @if (resolvedDashboard.dashboard.description) {
          <p class="workspace-dashboard__description">
            {{ resolvedDashboard.dashboard.description }}
          </p>
        }

      </header>

      @if (hasResolvedLayout()) {

        <section
          class="workspace-dashboard__layout"
          [attr.data-layout-id]="resolvedDashboard.layout?.id"
          [attr.data-layout-type]="resolvedDashboard.layout?.type">

          @for (
            region of resolvedDashboard.regions;
            track region.id
          ) {

            <section
              class="workspace-dashboard__region"
              [attr.data-region-id]="region.id"
              [attr.data-region-type]="region.regionType">

              <header class="workspace-dashboard__region-header">

                <h2 class="workspace-dashboard__region-title">
                  {{ region.title }}
                </h2>

                @if (region.description) {
                  <p class="workspace-dashboard__region-description">
                    {{ region.description }}
                  </p>
                }

              </header>

              <section
                class="workspace-dashboard__region-widgets"
                [dejaWorkspaceGridContainer]="
                  resolvedDashboard.gridConfiguration
                ">

                @for (
                  widget of widgetsForRegion(region);
                  track widget.id
                ) {

                  <deja-workspace-widget-host
                    [runtime]="runtime"
                    [widgetInstance]="widget"
                    [dejaWorkspaceGridItem]="widget.position" />

                }

              </section>

            </section>

          }

          @if (unassignedWidgets().length) {

            <section
              class="
                workspace-dashboard__region
                workspace-dashboard__region--unassigned
              "
              data-region-type="unassigned">

              <section
                class="workspace-dashboard__region-widgets"
                [dejaWorkspaceGridContainer]="
                  resolvedDashboard.gridConfiguration
                ">

                @for (
                  widget of unassignedWidgets();
                  track widget.id
                ) {

                  <deja-workspace-widget-host
                    [runtime]="runtime"
                    [widgetInstance]="widget"
                    [dejaWorkspaceGridItem]="widget.position" />

                }

              </section>

            </section>

          }

        </section>

      } @else {

        <section class="workspace-dashboard__widgets">

          @for (
            widget of resolvedDashboard.widgets;
            track widget.id
          ) {

            <deja-workspace-widget-host
              [runtime]="runtime"
              [widgetInstance]="widget"
              [dejaWorkspaceGridItem]="widget.position" />

          }

        </section>

      }

    </section>
  `,
  styles: `
    :host {
      display: block;
      width: 100%;
      height: 100%;
    }

    .workspace-dashboard {
      display: flex;
      flex-direction: column;
      width: 100%;
      min-height: 100%;
    }

    .workspace-dashboard__header {
      display: block;
    }

    .workspace-dashboard__title {
      margin: 0;
    }

    .workspace-dashboard__description {
      margin: 0;
    }

    .workspace-dashboard__layout {
      display: grid;
      grid-template-columns: repeat(
        auto-fit,
        minmax(min(100%, 20rem), 1fr)
      );
      align-items: start;
      flex: 1;
      width: 100%;
    }

    .workspace-dashboard__region {
      display: flex;
      flex-direction: column;
      min-width: 0;
      min-height: 0;
    }

    .workspace-dashboard__region-header {
      display: block;
    }

    .workspace-dashboard__region-title {
      margin: 0;
    }

    .workspace-dashboard__region-description {
      margin: 0;
    }

    .workspace-dashboard__region--unassigned {
      grid-column: 1 / -1;
    }

    /*
     * Dashboards legados permanecem utilizando composição
     * linear, sem dependência do Workspace Grid Renderer.
     */
    .workspace-dashboard__widgets {
      display: block;
      flex: 1;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceDashboardComponent
  implements OnInit, OnDestroy {

  private unsubscribeDashboardState?:
    WorkspaceDashboardStateUnsubscribe;

  constructor(
    private readonly changeDetectorRef: ChangeDetectorRef,
  ) {}

  /**
   * Runtime oficial do Workspace.
   */
  @Input({
    required: true,
  })
  runtime!: WorkspaceRuntime;

  /**
   * Dashboard completamente resolvido pelo Workspace Runtime.
   */
  @Input({
    required: true,
  })
  resolvedDashboard!: WorkspaceResolvedDashboard;

  /**
   * Estado institucional opcional utilizado para atualização
   * automática do Dashboard renderizado.
   *
   * Quando não informado, o componente permanece operando
   * exclusivamente com o Input legado.
   */
  @Input()
  dashboardState?: WorkspaceDashboardState;

  /**
   * Inicia a observação do Dashboard corrente quando um
   * Workspace Dashboard State for fornecido.
   */
  ngOnInit(): void {

    if (!this.dashboardState) {
      return;
    }

    this.unsubscribeDashboardState =
      this.dashboardState.subscribe(
        (update) => {

          this.resolvedDashboard = update.dashboard;

          this.changeDetectorRef.markForCheck();

        },
      );

  }

  /**
   * Encerra a inscrição institucional mantida pelo componente.
   */
  ngOnDestroy(): void {

    this.unsubscribeDashboardState?.();

    this.unsubscribeDashboardState = undefined;

  }

  /**
   * Verifica se o Dashboard possui Layout e regiões resolvidas.
   *
   * Dashboards sem Layout ou sem regiões permanecem utilizando
   * a composição linear legada.
   */
  protected hasResolvedLayout(): boolean {

    return (
      this.resolvedDashboard.layout !== undefined
      && this.resolvedDashboard.regions.length > 0
    );

  }

  /**
   * Retorna os Widgets pertencentes a uma região.
   */
  protected widgetsForRegion(
    region: WorkspaceLayoutRegion,
  ): readonly WorkspaceWidgetInstance[] {

    return this.resolvedDashboard.widgets.filter(
      (widget) => widget.regionId === region.id,
    );

  }

  /**
   * Retorna Widgets que não estão associados a uma região
   * efetivamente resolvida.
   *
   * Esse fallback preserva a compatibilidade durante a
   * transição de Dashboards legados para o Layout Engine.
   */
  protected unassignedWidgets(): readonly WorkspaceWidgetInstance[] {

    const regionIds = new Set(
      this.resolvedDashboard.regions.map(
        (region) => region.id,
      ),
    );

    return this.resolvedDashboard.widgets.filter(
      (widget) =>
        !widget.regionId
        || !regionIds.has(widget.regionId),
    );

  }

}