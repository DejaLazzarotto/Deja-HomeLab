import {
  ChangeDetectionStrategy,
  Component,
  inject,
} from '@angular/core';

import {
  Router,
} from '@angular/router';

import {
  AuthenticationService,
} from '../../../platform/authentication/application/authentication.service';

import {
  UserRole,
} from '../../../platform/authentication/domain/authenticated-user';

@Component({
  selector: 'deja-workspace-header',
  standalone: true,
  templateUrl: './workspace-header.html',
  styleUrl: './workspace-header.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceHeaderComponent {

  private readonly authentication =
    inject(AuthenticationService);

  private readonly router =
    inject(Router);

  readonly platformName = 'Deja Platform';

  readonly applicationName = 'Deja Indicadores';

  readonly user = this.authentication.user;

  roleLabel(
    role: UserRole,
  ): string {
    const labels: Record<UserRole, string> = {
      platform_admin: 'Administrador da plataforma',
      organization_admin: 'Administrador da organização',
      tenant_admin: 'Administrador do tenant',
      manager: 'Gestor',
      analyst: 'Analista',
      viewer: 'Visualizador',
    };

    return labels[role];
  }

  logout(): void {
    this.authentication.logout();

    void this.router.navigateByUrl('/login');
  }

}