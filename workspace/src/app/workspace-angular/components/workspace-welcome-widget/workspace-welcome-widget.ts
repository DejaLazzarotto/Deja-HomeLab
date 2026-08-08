/*
 * Deja Workspace Angular Integration
 *
 * Workspace Welcome Widget
 *
 * Primeiro Widget visual institucional da Deja Platform.
 * Atua como referência oficial para a construção dos futuros
 * Widgets corporativos da plataforma.
 */

import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

import { WorkspaceActionId } from '../../../core/workspace-sdk/runtime/workspace-action';

import { WorkspaceWidgetInstance } from '../../../core/workspace-sdk/runtime/workspace-widget';

import { WorkspaceWidgetContext } from '../../../core/workspace-sdk/runtime/workspace-widget-context';

import {
  WorkspaceButtonGroupComponent,
  WorkspaceGridComponent,
  WorkspaceIconButtonComponent,
  WorkspaceKpiCardComponent,
  WorkspacePanelComponent,
  WorkspaceSectionHeaderComponent,
  WorkspaceStackComponent,
  WorkspaceStatusBadgeComponent,
  WorkspaceStatusIndicatorComponent,
  WorkspaceSurfaceComponent,
  WorkspaceToolbarComponent,
  WorkspaceToolbarSpacerComponent,
} from '../widget-library/foundation';

/**
 * Componente visual institucional do Widget inicial
 * da Deja Platform.
 */
@Component({
  selector: 'deja-workspace-welcome-widget',
  standalone: true,
  imports: [
    WorkspaceGridComponent,
    WorkspaceStackComponent,
    WorkspaceSurfaceComponent,
    WorkspacePanelComponent,
    WorkspaceSectionHeaderComponent,
    WorkspaceStatusBadgeComponent,
    WorkspaceStatusIndicatorComponent,
    WorkspaceToolbarComponent,
    WorkspaceButtonGroupComponent,
    WorkspaceIconButtonComponent,
    WorkspaceToolbarSpacerComponent,
    WorkspaceKpiCardComponent,
  ],
  templateUrl: './workspace-welcome-widget.html',
  styleUrl: './workspace-welcome-widget.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceWelcomeWidgetComponent {

  protected readonly analyticsActionId: WorkspaceActionId =
    'deja.workspace.widget.welcome.analytics';

  protected readonly activityActionId: WorkspaceActionId =
    'deja.workspace.widget.welcome.activity';

  protected readonly timelineActionId: WorkspaceActionId =
    'deja.workspace.widget.welcome.timeline';
  /**
   * Instância declarativa do Widget no Dashboard.
   */
  @Input({
    required: true,
  })
  widgetInstance!: WorkspaceWidgetInstance;

  /**
   * Contexto institucional de execucao do Widget.
   */
  @Input({
    required: true,
  })
  widgetContext!: WorkspaceWidgetContext;

  /**
   * Mensagem configurada para esta instância.
   */
  protected get message(): string {
    const configuredMessage = this.widgetInstance.configuration?.['message'];

    if (typeof configuredMessage === 'string') {
      return configuredMessage;
    }

    return 'A infraestrutura inicial da Deja Platform ' + 'está funcionando corretamente.';
  }
  /**
   * Solicita a execucao de uma Action por meio
   * do contexto institucional do Widget.
   */
  protected executeAction(
    actionId: WorkspaceActionId,
  ): void {
    void this.widgetContext.dispatchAction(
      actionId,
    );
  }

}
