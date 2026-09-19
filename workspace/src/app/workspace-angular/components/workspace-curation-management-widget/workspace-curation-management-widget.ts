/*
 * Deja Workspace Angular Integration
 *
 * Curation Management Widget
 *
 * Integra a Curadoria do Deja Fotos ao Workspace institucional.
 */

import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';

import {
  CurationManagementComponent,
} from '../../../deja-fotos';

import {
  WorkspaceWidgetInstance,
} from '../../../core/workspace-sdk/runtime/workspace-widget';

import {
  WorkspaceWidgetContext,
} from '../../../core/workspace-sdk/runtime/workspace-widget-context';

@Component({
  selector: 'deja-workspace-curation-management-widget',
  standalone: true,
  imports: [
    CurationManagementComponent,
  ],
  template: `
    <deja-curation-management />
  `,
  styles: `
    :host {
      display: block;
      min-width: 0;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceCurationManagementWidgetComponent {
  @Input({
    required: true,
  })
  widgetInstance!: WorkspaceWidgetInstance;

  @Input({
    required: true,
  })
  widgetContext!: WorkspaceWidgetContext;
}