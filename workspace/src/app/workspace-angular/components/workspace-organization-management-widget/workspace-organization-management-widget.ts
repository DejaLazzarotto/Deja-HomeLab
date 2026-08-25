import {
  HttpClient,
} from '@angular/common/http';

import {
  ChangeDetectionStrategy,
  Component,
  Input,
  inject,
} from '@angular/core';

import {
  ModuleManagementComposition,
  OrganizationManagementComponent,
} from '../../../platform/module-management';

import {
  WorkspaceWidgetInstance,
} from '../../../core/workspace-sdk/runtime/workspace-widget';

import {
  WorkspaceWidgetContext,
} from '../../../core/workspace-sdk/runtime/workspace-widget-context';

@Component({
  selector: 'deja-workspace-organization-management-widget',
  standalone: true,
  imports: [
    OrganizationManagementComponent,
  ],
  template: `
    <deja-organization-management
      [service]="composition.service"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceOrganizationManagementWidgetComponent {

  private readonly http = inject(HttpClient);

  protected readonly composition =
    new ModuleManagementComposition(this.http);

  @Input({
    required: true,
  })
  widgetInstance!: WorkspaceWidgetInstance;

  @Input({
    required: true,
  })
  widgetContext!: WorkspaceWidgetContext;

}