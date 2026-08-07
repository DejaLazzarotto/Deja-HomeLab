/*
 * Deja Workspace Angular Integration
 *
 * Workspace Welcome Widget
 *
 * Primeiro Widget visual institucional da Deja Platform.
 * Atua como referência oficial para a construção dos futuros
 * Widgets corporativos da plataforma.
 */

import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';

import {
  WorkspaceWidgetInstance,
} from '../../../core/workspace-sdk/runtime/workspace-widget';

import {
  WorkspaceGridComponent,
  WorkspacePanelComponent,
  WorkspaceSectionHeaderComponent,
  WorkspaceStackComponent,
  WorkspaceStatusBadgeComponent,
  WorkspaceStatusIndicatorComponent,
  WorkspaceSurfaceComponent,
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
  ],
  templateUrl: './workspace-welcome-widget.html',
  styleUrl: './workspace-welcome-widget.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceWelcomeWidgetComponent {

  /**
   * Instância declarativa do Widget no Dashboard.
   */
  @Input({
    required: true,
  })
  widgetInstance!: WorkspaceWidgetInstance;

  /**
   * Mensagem configurada para esta instância.
   */
  protected get message(): string {

    const configuredMessage =
      this.widgetInstance.configuration?.['message'];

    if (typeof configuredMessage === 'string') {
      return configuredMessage;
    }

    return (
      'A infraestrutura inicial da Deja Platform '
      + 'está funcionando corretamente.'
    );
  }

}