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

import {
  WorkspaceNavigation,
} from '../../../core/workspace-sdk/runtime/workspace-navigation';

import {
  WorkspaceBootstrapService,
} from '../../bootstrap/workspace-bootstrap.service';

import {
  WorkspaceIconProvider,
} from '../../services/workspace-icon-provider';

/**
 * Sidebar permanente da Workspace Shell.
 *
 * A Sidebar não mantém conhecimento sobre Dashboards,
 * aplicações ou rotas específicas.
 *
 * Toda navegação é resolvida exclusivamente pelo
 * Workspace Runtime através dos Registries institucionais.
 */
@Component({
  selector: 'deja-workspace-sidebar',
  standalone: true,
  templateUrl: './workspace-sidebar.html',
  styleUrl: './workspace-sidebar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceSidebarComponent {

  constructor(
    private readonly bootstrapService: WorkspaceBootstrapService,
    readonly iconProvider: WorkspaceIconProvider,
  ) {}

  /**
   * Runtime oficial do Workspace.
   *
   * Obtido através do Bootstrap Service,
   * preservando o Composition Root como único
   * ponto responsável pela composição.
   */
  private get runtime() {

    return this.bootstrapService.getRuntime();

  }

  /**
   * Retorna as navegações institucionais habilitadas.
   *
   * A Sidebar consome exclusivamente o Registry
   * através da API pública do Runtime.
   */
  get navigation(): readonly WorkspaceNavigation[] {

    return this.runtime.visibleNavigations();

  }

  /**
   * Executa uma navegação institucional.
   */
  async navigate(
    navigation: WorkspaceNavigation,
  ): Promise<void> {

    await this.runtime.navigate(
      navigation.id,
    );

  }

  /**
   * Verifica se a navegação está ativa.
   */
  isActive(
    navigation: WorkspaceNavigation,
  ): boolean {

    return this.runtime.isNavigationActive(
      navigation.id,
    );

  }

  /**
   * Resolve o recurso físico do ícone institucional.
   */
  resolveIcon(
    navigation: WorkspaceNavigation,
  ): string | undefined {

    return this.iconProvider.resolve(
      navigation.icon,
    );

  }

}