/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Capability Resolver
 *
 * Responsável pela resolução institucional das capacidades
 * declarativas de um Workspace Layout.
 */

import {
  WorkspaceLayout,
} from './workspace-layout';

import {
  WorkspaceLayoutCapabilities,
} from './workspace-layout-capabilities';

/**
 * Responsável pela resolução institucional das capacidades
 * de um Workspace Layout.
 */
export class WorkspaceLayoutCapabilityResolver {

  /**
   * Resolve as capacidades institucionais de um Workspace Layout.
   */
  resolve(
    layout: WorkspaceLayout | undefined,
  ): WorkspaceLayoutCapabilities {

    const capabilities = layout?.capabilities;

    return {
      resizable: capabilities?.resizable ?? false,
      movable: capabilities?.movable ?? false,
      responsive: capabilities?.responsive ?? true,
      editable: capabilities?.editable ?? false,
    };
  }

}