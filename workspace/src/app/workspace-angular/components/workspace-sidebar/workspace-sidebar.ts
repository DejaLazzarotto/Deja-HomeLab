/*
 * Deja Workspace Angular Integration
 *
 * Workspace Sidebar Component
 *
 * Barra lateral institucional responsável pela navegação
 * principal da Deja Platform.
 */

import {
  ChangeDetectionStrategy,
  Component,
} from '@angular/core';

/**
 * Item institucional de navegação.
 */
interface WorkspaceNavigationItem {

  readonly id: string;

  readonly title: string;

  readonly icon: string;

}

/**
 * Sidebar permanente da Workspace Shell.
 */
@Component({
  selector: 'deja-workspace-sidebar',
  standalone: true,
  templateUrl: './workspace-sidebar.html',
  styleUrl: './workspace-sidebar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceSidebarComponent {

  /**
   * Navegação institucional inicial.
   *
   * Nesta fase ainda não existe integração com Commands,
   * Actions ou Dashboards. Os itens servem para estabelecer
   * a estrutura visual definitiva da Shell.
   */
  readonly navigation: readonly WorkspaceNavigationItem[] = [
    {
      id: 'dashboard',
      title: 'Dashboard',
      icon: '⌂',
    },
    {
      id: 'applications',
      title: 'Applications',
      icon: '◫',
    },
    {
      id: 'reports',
      title: 'Reports',
      icon: '▤',
    },
    {
      id: 'settings',
      title: 'Settings',
      icon: '⚙',
    },
  ];

}