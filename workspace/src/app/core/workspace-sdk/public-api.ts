/*
 * Deja Workspace UI SDK
 *
 * Public API v1
 *
 * Este é o único ponto oficial de exportação do Workspace SDK.
 * Implementações internas não devem ser importadas diretamente
 * por aplicações ou módulos externos.
 */

export * from './runtime/workspace-runtime';

export * from './runtime/workspace-runtime-registry';

export * from './runtime/workspace-runtime-events';
export * from './runtime/workspace-runtime-event-dispatcher';

export * from './runtime/workspace-runtime-hooks';
export * from './runtime/workspace-runtime-hook-dispatcher';

export * from './runtime/workspace-runtime-extension-point';
export * from './runtime/workspace-runtime-extension-registry';
export * from './runtime/workspace-runtime-extension-dispatcher';

export * from './services/workspace-services';

export * from './runtime/workspace-command';
export * from './runtime/workspace-command-registry';
export * from './runtime/workspace-command-dispatcher';

export * from './runtime/workspace-action';
export * from './runtime/workspace-action-registry';
export * from './runtime/workspace-action-dispatcher';

export * from './ui/workspace-menu';
export * from './ui/workspace-menu-registry';
export * from './ui/workspace-toolbar';
export * from './ui/workspace-toolbar-registry';
export * from './ui/workspace-context-menu';
export * from './ui/workspace-context-menu-registry';