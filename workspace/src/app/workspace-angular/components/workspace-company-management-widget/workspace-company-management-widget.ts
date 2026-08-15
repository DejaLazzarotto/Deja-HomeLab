/*
 * Deja Workspace Angular Integration
 *
 * Company Management Widget
 *
 * Integra a Gestão de Empresas ao Workspace institucional.
 */

import {
  HttpClient,
} from '@angular/common/http';

import {
  ChangeDetectionStrategy,
  Component,
  Input,
  OnInit,
  inject,
  signal,
} from '@angular/core';

import {
  firstValueFrom,
} from 'rxjs';

import {
  AuthenticationService,
} from '../../../deja-indicadores/authentication/application/authentication.service';

import {
  CompaniesComposition,
  CompanyEnvironmentOption,
  CompanyListComponent,
} from '../../../deja-indicadores/companies';

import {
  WorkspaceWidgetInstance,
} from '../../../core/workspace-sdk/runtime/workspace-widget';

import {
  WorkspaceWidgetContext,
} from '../../../core/workspace-sdk/runtime/workspace-widget-context';

interface EnvironmentResponse {
  readonly id: string;
  readonly tenant_id: string;
  readonly name: string;
  readonly status: string;
  readonly created_at: string;
  readonly updated_at: string;
}

@Component({
  selector: 'deja-workspace-company-management-widget',
  standalone: true,
  imports: [
    CompanyListComponent,
  ],
  template: `
    <deja-company-list
      [service]="composition.service"
      [environments]="environments()"
      [defaultEnvironmentId]="currentUser?.environmentId ?? null"
      [canManage]="canManage"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceCompanyManagementWidgetComponent
implements OnInit {

  private readonly http = inject(HttpClient);

  private readonly authentication =
    inject(AuthenticationService);

  protected readonly currentUser =
    this.authentication.user();

  protected readonly composition =
    new CompaniesComposition(
      this.http,
    );

  protected readonly environments =
    signal<readonly CompanyEnvironmentOption[]>([]);

  protected readonly canManage = [
    'platform_admin',
    'organization_admin',
    'tenant_admin',
    'manager',
  ].includes(
    this.currentUser?.role ?? '',
  );

  @Input({
    required: true,
  })
  widgetInstance!: WorkspaceWidgetInstance;

  @Input({
    required: true,
  })
  widgetContext!: WorkspaceWidgetContext;

  ngOnInit(): void {
    if (this.canManage) {
      void this.loadEnvironments();
    }
  }

  private async loadEnvironments(): Promise<void> {
    try {
      const response = await firstValueFrom(
        this.http.get<readonly EnvironmentResponse[]>(
          '/api/v1/environments',
        ),
      );

      this.environments.set(
        response.map(environment => ({
          id: environment.id,
          name: environment.name,
        })),
      );
    } catch {
      const environmentId =
        this.currentUser?.environmentId;

      if (environmentId) {
        this.environments.set([
          {
            id: environmentId,
            name: 'Ambiente atual',
          },
        ]);
      }
    }
  }

}