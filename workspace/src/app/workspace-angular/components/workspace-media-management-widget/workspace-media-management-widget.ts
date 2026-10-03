/*
 * Deja Workspace Angular Integration
 *
 * Media Management Widget
 *
 * Integra o Album Admin de mídias ao Workspace institucional.
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
  AlbumsComposition,
  FotosEnvironmentOption,
  MediaComposition,
  MediaManagementComponent,
} from '../../../deja-fotos';

import {
  AuthenticationService,
} from '../../../platform/authentication/application/authentication.service';

import {
  getModuleRole,
} from '../../../platform/module-management/application/module-access';

import {
  WorkspaceWidgetInstance,
} from '../../../core/workspace-sdk/runtime/workspace-widget';

import {
  WorkspaceWidgetContext,
} from '../../../core/workspace-sdk/runtime/workspace-widget-context';

interface EnvironmentResponse {
  readonly id: string;
  readonly name: string;
}

@Component({
  selector: 'deja-workspace-media-management-widget',
  standalone: true,
  imports: [
    MediaManagementComponent,
  ],
  template: `
    @if (loadingEnvironments()) {
      <div class="scope-state">
        Carregando ambientes...
      </div>
    } @else if (currentUser) {
      @if (environmentError()) {
        <div class="scope-state scope-state--warning">
          <span>{{ environmentError() }}</span>

          <button
            type="button"
            (click)="loadEnvironments()"
          >
            Tentar novamente
          </button>
        </div>
      }

      <deja-media-management
        [mediaService]="mediaComposition.service"
        [albumService]="albumsComposition.service"
        [environments]="environments()"
        [defaultEnvironmentId]="currentUser.environmentId"
        [canUpload]="canUpload"
        [canCurate]="canCurate"
      />
    }
  `,
  styles: `
    :host {
      display: block;
      min-width: 0;
    }

    .scope-state {
      padding: var(--workspace-spacing-lg);
      color: var(--workspace-color-text-secondary);
      font-size: 0.82rem;
      text-align: center;
      background: var(--workspace-color-surface);
      border: 1px solid var(--workspace-color-border);
      border-radius: var(--workspace-radius-lg);
    }

    .scope-state--warning {
      display: flex;
      gap: var(--workspace-spacing-md);
      align-items: center;
      justify-content: space-between;
      margin-bottom: var(--workspace-spacing-md);
      color: #92400e;
      text-align: left;
      background: #fffbeb;
      border-color: #fde68a;
    }

    .scope-state button {
      min-height: 2.25rem;
      padding: 0.5rem 0.75rem;
      color: var(--workspace-color-primary);
      font: inherit;
      font-size: 0.74rem;
      font-weight: 800;
      cursor: pointer;
      background: transparent;
      border: 1px solid currentColor;
      border-radius: var(--workspace-radius-md);
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceMediaManagementWidgetComponent
  implements OnInit {
  private readonly http = inject(HttpClient);

  private readonly authentication =
    inject(AuthenticationService);

  protected readonly currentUser =
    this.authentication.user();

  protected readonly mediaComposition =
    new MediaComposition(this.http);

  protected readonly albumsComposition =
    new AlbumsComposition(this.http);

  protected readonly environments =
    signal<readonly FotosEnvironmentOption[]>([]);

  protected readonly loadingEnvironments =
    signal(false);

  protected readonly environmentError =
    signal<string | null>(null);

  protected readonly fotosRole =
    getModuleRole(this.currentUser, 'fotos');

  protected readonly canUpload =
    this.currentUser?.role === 'platform_admin'
    || this.fotosRole === 'manager';

  protected readonly canCurate =
    this.currentUser?.role === 'platform_admin'
    || this.fotosRole === 'manager';

  @Input({
    required: true,
  })
  widgetInstance!: WorkspaceWidgetInstance;

  @Input({
    required: true,
  })
  widgetContext!: WorkspaceWidgetContext;

  ngOnInit(): void {
    void this.loadEnvironments();
  }

  protected async loadEnvironments(): Promise<void> {
    this.loadingEnvironments.set(true);
    this.environmentError.set(null);

    try {
      const environments = await firstValueFrom(
        this.http.get<readonly EnvironmentResponse[]>(
          '/api/v1/environments',
        ),
      );

      this.environments.set(
        environments.map(environment => ({
          id: environment.id,
          name: environment.name,
        })),
      );
    } catch {
      this.environmentError.set(
        'Não foi possível carregar os nomes dos ambientes. A consulta de mídias continua disponível.',
      );
    } finally {
      this.loadingEnvironments.set(false);
    }
  }
}