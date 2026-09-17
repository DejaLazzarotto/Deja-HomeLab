/*
 * Deja Workspace Angular Integration
 *
 * Workspace Sidebar Component
 */

import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  ViewChild,
} from '@angular/core';

import {
  canAccessAdministration,
} from '../../../platform/authentication/application/administration.guard';

import {
  AuthenticationService,
} from '../../../platform/authentication/application/authentication.service';

import {
  canAccessUserAdministration,
} from '../../../platform/authentication/application/user-administration.guard';

import {
  canAccessModule,
} from '../../../platform/module-management/application/module-access';

import {
  isModuleKey,
} from '../../../platform/module-management/domain/module-key';

import {
  WorkspaceNavigation,
} from '../../../core/workspace-sdk/runtime/workspace-navigation';

import {
  WorkspaceBootstrapService,
} from '../../bootstrap/workspace-bootstrap.service';

import {
  WorkspaceIconProvider,
} from '../../services/workspace-icon-provider';

import {
  WorkspaceShellController,
} from '../../services/workspace-shell-controller';

type NavigationSectionId =
  | 'home'
  | 'administration'
  | 'operation'
  | 'chamados'
  | 'fotos'
  | 'analysis';

interface NavigationSection {
  readonly id: NavigationSectionId;
  readonly title: string | null;
  readonly items: readonly WorkspaceNavigation[];
}

/**
 * Mantém a posição vertical do menu enquanto a aplicação
 * permanece carregada. O estado sobrevive à recriação do
 * componente causada pelas trocas de rota do Workspace.
 */
let navigationScrollTop = 0;

@Component({
  selector: 'deja-workspace-sidebar',
  standalone: true,
  templateUrl: './workspace-sidebar.html',
  styleUrl: './workspace-sidebar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceSidebarComponent
  implements AfterViewInit {

  @ViewChild(
    'navigation',
    {
      static: true,
    },
  )
  private readonly navigationElement!:
    ElementRef<HTMLElement>;

  private readonly administrationNavigationId =
    'deja.workspace.navigation.administration';

  private readonly usersNavigationId =
    'deja.workspace.navigation.administration.users';

  private readonly platformOrganizationsNavigationId =
    'deja.workspace.navigation.platform.organizations';

  private readonly sectionDefinitions: readonly {
    id: NavigationSectionId;
    title: string | null;
  }[] = [
    {
      id: 'home',
      title: null,
    },
    {
      id: 'administration',
      title: 'Administração',
    },
    {
      id: 'operation',
      title: 'Operação',
    },
    {
      id: 'chamados',
      title: 'Chamados',
    },
    {
      id: 'fotos',
      title: 'Fotos',
    },
    {
      id: 'analysis',
      title: 'Análise',
    },
  ];

  constructor(
    private readonly authentication:
      AuthenticationService,
    private readonly bootstrapService:
      WorkspaceBootstrapService,
    private readonly shell:
      WorkspaceShellController,
    readonly iconProvider:
      WorkspaceIconProvider,
  ) {}

  private get runtime() {
    return this.bootstrapService.getRuntime();
  }

  get navigationSections(): readonly NavigationSection[] {
    const user = this.authentication.user();

    const navigation = this.runtime
      .visibleNavigations()
      .filter(item => {
        if (item.id === this.administrationNavigationId) {
          return (
            user !== null
            && canAccessAdministration(user.role)
          );
        }

        if (item.id === this.usersNavigationId) {
          return (
            user !== null
            && canAccessUserAdministration(user.role)
          );
        }

        if (
          item.id === this.platformOrganizationsNavigationId
        ) {
          return user?.role === 'platform_admin';
        }

        const moduleKey = item.metadata?.['moduleKey'];

        if (isModuleKey(moduleKey)) {
          return canAccessModule(user, moduleKey);
        }

        return true;
      });

    return this.sectionDefinitions
      .map(section => ({
        ...section,
        items: navigation.filter(
          item => item.metadata?.['section'] === section.id,
        ),
      }))
      .filter(section => section.items.length > 0);
  }

  ngAfterViewInit(): void {
    this.navigationElement.nativeElement.scrollTop =
      navigationScrollTop;
  }

  rememberScrollPosition(): void {
    navigationScrollTop =
      this.navigationElement.nativeElement.scrollTop;
  }

  async navigate(
    navigation: WorkspaceNavigation,
  ): Promise<void> {
    this.rememberScrollPosition();

    await this.shell.navigate(
      navigation.id,
    );
  }

  isActive(
    navigation: WorkspaceNavigation,
  ): boolean {
    return this.runtime.isNavigationActive(
      navigation.id,
    );
  }

  resolveIcon(
    navigation: WorkspaceNavigation,
  ): string | undefined {
    return this.iconProvider.resolve(
      navigation.icon,
    );
  }

}