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
  AuthenticationService,
} from '../../../platform/authentication/application/authentication.service';

import {
  canAccessModule,
} from '../../../platform/module-management/application/module-access';

import {
  isModuleKey,
} from '../../../platform/module-management/domain/module-key';

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
  templateUrl: './workspace-dashboard.html',
  styleUrl: './workspace-dashboard.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceDashboardComponent
implements OnInit, OnDestroy {

  private unsubscribeDashboardState?:
    WorkspaceDashboardStateUnsubscribe;


  constructor(
    private readonly authentication:
      AuthenticationService,
    private readonly changeDetectorRef:
      ChangeDetectorRef,
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

          this.resolvedDashboard =
            update.dashboard;


          this.changeDetectorRef.markForCheck();

        },
      );

  }


  /**
   * Encerra a inscrição institucional mantida pelo componente.
   */
  ngOnDestroy(): void {

    this.unsubscribeDashboardState?.();


    this.unsubscribeDashboardState =
      undefined;

  }


  /**
   * Retorna os Widgets permitidos para a sessão atual.
   */
  protected visibleWidgets():
    readonly WorkspaceWidgetInstance[] {

    const user = this.authentication.user();


    return this.resolvedDashboard.widgets.filter(
      (widgetInstance) => {

        const widget = this.runtime.requireWidget(
          widgetInstance.widgetId,
        );

        const moduleKey =
          widget.metadata?.['moduleKey'];


        return (
          !isModuleKey(moduleKey)
          || canAccessModule(user, moduleKey)
        );

      },
    );

  }


  /**
   * Indica se existe ao menos um Widget visível.
   */
  protected hasVisibleWidgets(): boolean {

    return this.visibleWidgets().length > 0;

  }


  /**
   * Indica se o Dashboard deve apresentar somente seu conteúdo,
   * sem os cabeçalhos e molduras institucionais intermediárias.
   */
  protected get chromeHidden(): boolean {

    return (
      this.resolvedDashboard
        .dashboard
        .metadata?.['hideChrome']
      === true
    );

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
   * Retorna os Widgets permitidos pertencentes a uma região.
   */
  protected widgetsForRegion(
    region: WorkspaceLayoutRegion,
  ): readonly WorkspaceWidgetInstance[] {

    return this.visibleWidgets().filter(
      (widget) =>
        widget.regionId === region.id,
    );

  }


  /**
   * Retorna Widgets permitidos que não estão associados a uma
   * região efetivamente resolvida.
   *
   * Esse fallback preserva a compatibilidade durante a
   * transição de Dashboards legados para o Layout Engine.
   */
  protected unassignedWidgets():
    readonly WorkspaceWidgetInstance[] {

    const regionIds =
      new Set(
        this.resolvedDashboard.regions.map(
          (region) => region.id,
        ),
      );


    return this.visibleWidgets().filter(
      (widget) =>
        !widget.regionId
        || !regionIds.has(widget.regionId),
    );

  }

}