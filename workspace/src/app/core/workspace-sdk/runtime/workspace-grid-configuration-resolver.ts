/*
 * Deja Workspace UI SDK
 *
 * Workspace Grid Configuration Resolver
 *
 * Responsável pela resolução institucional da configuração
 * utilizada pela infraestrutura de renderização do Workspace Grid.
 */

import {
  WorkspaceGridConfiguration,
} from './workspace-grid-configuration';

import {
  WorkspaceLayout,
} from './workspace-layout';

import {
  WorkspaceLayoutConfiguration,
} from './workspace-layout-configuration';

/**
 * Responsável pela resolução institucional da configuração
 * do Workspace Grid.
 */
export class WorkspaceGridConfigurationResolver {

  /**
   * Resolve a configuração institucional do Workspace Grid.
   */
  resolve(
    layout: WorkspaceLayout | undefined,
  ): WorkspaceGridConfiguration {

    const configuration: WorkspaceLayoutConfiguration | undefined =
      layout?.configuration;

    const grid = configuration?.grid;

    return {
      columns: grid?.columns ?? 12,
      columnGap: grid?.columnGap ?? '1rem',
      rowGap: grid?.rowGap ?? '1rem',
      autoRowSize: grid?.autoRowSize ?? 'minmax(4rem, auto)',
      autoFlow: grid?.autoFlow ?? 'row dense',
    };
  }

}