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
  OnInit,
  inject,
  signal,
} from '@angular/core';

import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { AuthenticationService } from '../../../platform/authentication/application/authentication.service';

import {
  CurationManagementComponent,
  FotosEnvironmentOption,
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
    <deja-curation-management
      [environments]="environments()"
      [defaultEnvironmentId]="user?.environmentId ?? null"
      [canManage]="canManage"
    />
  `,
  styles: `
    :host {
      display: block;
      min-width: 0;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceCurationManagementWidgetComponent implements OnInit {
  private readonly http = inject(HttpClient);
  protected readonly user = inject(AuthenticationService).user();
  protected readonly environments = signal<readonly FotosEnvironmentOption[]>([]);
  protected readonly canManage = [
    'platform_admin', 'organization_admin', 'tenant_admin', 'manager',
  ].includes(this.user?.role ?? '');

  async ngOnInit(): Promise<void> {
    try {
      this.environments.set(await firstValueFrom(this.http.get<readonly FotosEnvironmentOption[]>(
        '/api/v1/environments',
      )));
    } catch {
      // A página ainda permite listar mídias do escopo autorizado.
    }
  }
  @Input({
    required: true,
  })
  widgetInstance!: WorkspaceWidgetInstance;

  @Input({
    required: true,
  })
  widgetContext!: WorkspaceWidgetContext;
}
