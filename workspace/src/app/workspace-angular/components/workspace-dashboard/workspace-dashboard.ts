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

import { WorkspaceLayoutRegion } from '../../../core/workspace-sdk/runtime/workspace-layout-region';

import { WorkspaceResolvedDashboard } from '../../../core/workspace-sdk/runtime/workspace-resolved-dashboard';

import { WorkspaceRuntime } from '../../../core/workspace-sdk/runtime/workspace-runtime';

import { WorkspaceWidgetInstance } from '../../../core/workspace-sdk/runtime/workspace-widget';

import { WorkspaceGridContainerDirective } from '../../rendering/workspace-grid-container.directive';

import { WorkspaceGridItemDirective } from '../../rendering/workspace-grid-item.directive';

import { WorkspaceWidgetHostComponent } from '../workspace-widget-host/workspace-widget-host';

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
          [attr.data-layout-type]="resolvedDashboard.layout?.type"
        >
          @for (region of resolvedDashboard.regions; track region.id) {
            <section
              class="workspace-dashboard__region"
              [attr.data-region-id]="region.id"
              [attr.data-region-type]="region.regionType"
            >
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
                [dejaWorkspaceGridContainer]="resolvedDashboard.gridConfiguration"
              >
                @for (widget of widgetsForRegion(region); track widget.id) {
                  <deja-workspace-widget-host
                    [runtime]="runtime"
                    [widgetInstance]="widget"
                    [dejaWorkspaceGridItem]="widget.position"
                  />
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
              data-region-type="unassigned"
            >
              <section
                class="workspace-dashboard__region-widgets"
                [dejaWorkspaceGridContainer]="resolvedDashboard.gridConfiguration"
              >
                @for (widget of unassignedWidgets(); track widget.id) {
                  <deja-workspace-widget-host
                    [runtime]="runtime"
                    [widgetInstance]="widget"
                    [dejaWorkspaceGridItem]="widget.position"
                  />
                }
              </section>
            </section>
          }
        </section>
      } @else {
        <section class="workspace-dashboard__widgets">
          @for (widget of resolvedDashboard.widgets; track widget.id) {
            <deja-workspace-widget-host
              [runtime]="runtime"
              [widgetInstance]="widget"
              [dejaWorkspaceGridItem]="widget.position"
            />
          }
        </section>
      }
    </section>
  `,
  styles: `
    :host {
      display: block;
      width: 100%;
      min-width: 0;
      min-height: 100%;
    }

    .workspace-dashboard {
      display: flex;
      flex-direction: column;
      gap: var(--workspace-spacing-lg);
      width: 100%;
      min-width: 0;
      min-height: 100%;
    }

    .workspace-dashboard__header {
      position: relative;
      display: flex;
      flex-direction: column;
      gap: var(--workspace-spacing-sm);
      min-width: 0;
      padding: var(--workspace-spacing-lg) var(--workspace-spacing-xl);
      overflow: hidden;
      border: 1px solid var(--workspace-color-border);
      border-radius: var(--workspace-radius-xl);
      background: linear-gradient(
        135deg,
        rgb(24 36 56 / 94%) 0%,
        rgb(16 24 39 / 94%) 58%,
        rgb(13 20 34 / 96%) 100%
      );
      box-shadow:
        var(--workspace-shadow-md),
        inset 0 1px 0 rgb(255 255 255 / 4%);
    }

    .workspace-dashboard__header::before {
      position: absolute;
      top: -8rem;
      right: -5rem;
      width: 22rem;
      height: 22rem;
      pointer-events: none;
      border-radius: 50%;
      content: '';
      background: radial-gradient(
        circle,
        rgb(79 140 255 / 18%) 0%,
        rgb(79 140 255 / 5%) 42%,
        transparent 70%
      );
    }

    .workspace-dashboard__header::after {
      position: absolute;
      bottom: 0;
      left: var(--workspace-spacing-xl);
      width: 4rem;
      height: 0.1875rem;
      border-radius: var(--workspace-radius-pill);
      content: '';
      background: linear-gradient(
        90deg,
        var(--workspace-color-primary),
        var(--workspace-color-accent)
      );
      box-shadow: 0 0 18px var(--workspace-color-primary-glow);
    }

    .workspace-dashboard__title {
      position: relative;
      margin: 0;
      color: var(--workspace-color-text);
      font-size: clamp(var(--workspace-font-size-xl), 2vw, var(--workspace-font-size-2xl));
      font-weight: var(--workspace-font-weight-bold);
      line-height: var(--workspace-line-height-tight);
      letter-spacing: var(--workspace-letter-spacing-tight);
      z-index: 1;
    }

    .workspace-dashboard__description {
      position: relative;
      max-width: 52rem;
      margin: 0;
      color: var(--workspace-color-text-secondary);
      font-size: var(--workspace-font-size-sm);
      line-height: var(--workspace-line-height-default);
      z-index: 1;
    }

    .workspace-dashboard__layout {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 22rem), 1fr));
      align-items: start;
      gap: var(--workspace-spacing-lg);
      flex: 1;
      width: 100%;
      min-width: 0;
    }

    .workspace-dashboard__region {
      display: flex;
      flex-direction: column;
      gap: var(--workspace-spacing-md);
      min-width: 0;
      min-height: 0;
      padding: var(--workspace-spacing-lg);
      border: 1px solid var(--workspace-color-border);
      border-radius: var(--workspace-radius-xl);
      background: linear-gradient(145deg, rgb(20 30 47 / 88%) 0%, rgb(15 23 37 / 92%) 100%);
      box-shadow:
        var(--workspace-shadow-sm),
        inset 0 1px 0 rgb(255 255 255 / 3%);
      transition:
        border-color var(--workspace-transition-default),
        box-shadow var(--workspace-transition-default);
    }

    .workspace-dashboard__region:hover {
      border-color: var(--workspace-color-border-strong);
      box-shadow:
        var(--workspace-shadow-md),
        inset 0 1px 0 rgb(255 255 255 / 4%);
    }

    .workspace-dashboard__region-header {
      display: flex;
      flex-direction: column;
      gap: var(--workspace-spacing-xs);
      min-width: 0;
      padding-bottom: var(--workspace-spacing-md);
      border-bottom: 1px solid var(--workspace-color-border-soft);
    }

    .workspace-dashboard__region-title {
      margin: 0;
      overflow: hidden;
      color: var(--workspace-color-text);
      font-size: var(--workspace-font-size-md);
      font-weight: var(--workspace-font-weight-semibold);
      line-height: var(--workspace-line-height-tight);
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .workspace-dashboard__region-description {
      margin: 0;
      color: var(--workspace-color-text-muted);
      font-size: var(--workspace-font-size-xs);
      line-height: var(--workspace-line-height-default);
    }

    .workspace-dashboard__region-widgets {
      min-width: 0;
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
      min-width: 0;
      padding: var(--workspace-spacing-lg);
      border: 1px solid var(--workspace-color-border);
      border-radius: var(--workspace-radius-xl);
      background: linear-gradient(145deg, rgb(20 30 47 / 88%) 0%, rgb(15 23 37 / 92%) 100%);
      box-shadow:
        var(--workspace-shadow-sm),
        inset 0 1px 0 rgb(255 255 255 / 3%);
    }

    @media (max-width: 48rem) {
      .workspace-dashboard {
        gap: var(--workspace-spacing-md);
      }

      .workspace-dashboard__header {
        padding: var(--workspace-spacing-lg);
      }

      .workspace-dashboard__header::after {
        left: var(--workspace-spacing-lg);
      }

      .workspace-dashboard__layout {
        gap: var(--workspace-spacing-md);
      }

      .workspace-dashboard__region,
      .workspace-dashboard__widgets {
        padding: var(--workspace-spacing-md);
      }
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceDashboardComponent implements OnInit, OnDestroy {
  private unsubscribeDashboardState?: WorkspaceDashboardStateUnsubscribe;

  constructor(private readonly changeDetectorRef: ChangeDetectorRef) {}

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

    this.unsubscribeDashboardState = this.dashboardState.subscribe((update) => {
      this.resolvedDashboard = update.dashboard;

      this.changeDetectorRef.markForCheck();
    });
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
    return this.resolvedDashboard.layout !== undefined && this.resolvedDashboard.regions.length > 0;
  }

  /**
   * Retorna os Widgets pertencentes a uma região.
   */
  protected widgetsForRegion(region: WorkspaceLayoutRegion): readonly WorkspaceWidgetInstance[] {
    return this.resolvedDashboard.widgets.filter((widget) => widget.regionId === region.id);
  }

  /**
   * Retorna Widgets que não estão associados a uma região
   * efetivamente resolvida.
   *
   * Esse fallback preserva a compatibilidade durante a
   * transição de Dashboards legados para o Layout Engine.
   */
  protected unassignedWidgets(): readonly WorkspaceWidgetInstance[] {
    const regionIds = new Set(this.resolvedDashboard.regions.map((region) => region.id));

    return this.resolvedDashboard.widgets.filter(
      (widget) => !widget.regionId || !regionIds.has(widget.regionId),
    );
  }
}
