/*
 * Deja Workspace Angular Integration
 *
 * Workspace Sidebar Component
 */

import {
  ChangeDetectionStrategy,
  Component,
} from '@angular/core';

import {
  canAccessAdministration,
} from '../../../deja-indicadores/authentication/application/administration.guard';

import {
  AuthenticationService,
} from '../../../deja-indicadores/authentication/application/authentication.service';

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
  | 'analysis';

interface NavigationSection {
  readonly id: NavigationSectionId;
  readonly title: string | null;
  readonly items: readonly WorkspaceNavigation[];
}

@Component({
  selector: 'deja-workspace-sidebar',
  standalone: true,
  templateUrl: './workspace-sidebar.html',
  styleUrl: './workspace-sidebar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceSidebarComponent {

  private readonly administrationNavigationId =
    'deja.workspace.navigation.administration';

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
      .filter(item => (
        item.id !== this.administrationNavigationId
        || (
          user !== null
          && canAccessAdministration(user.role)
        )
      ));

    return this.sectionDefinitions
      .map(section => ({
        ...section,
        items: navigation.filter(
          item => item.metadata?.['section'] === section.id,
        ),
      }))
      .filter(section => section.items.length > 0);
  }

  async navigate(
    navigation: WorkspaceNavigation,
  ): Promise<void> {
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