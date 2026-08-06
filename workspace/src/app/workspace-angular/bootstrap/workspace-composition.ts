/*
 * Deja Workspace Angular Integration
 *
 * Workspace Composition
 *
 * Composition Root institucional responsável pela composição
 * completa da infraestrutura do Workspace.
 *
 * Esta classe representa o único ponto autorizado para criação
 * dos componentes estruturais da plataforma, preservando o
 * desacoplamento entre Bootstrap, Runtime e infraestrutura.
 */

import {
  WorkspaceRegistries,
} from '../../core/workspace-sdk/registries/workspace-registries';

import {
  WorkspaceEditingFactory,
} from '../../core/workspace-sdk/runtime/workspace-editing-factory';

import {
  WorkspaceLayoutEventDispatcher,
} from '../../core/workspace-sdk/runtime/workspace-layout-event-dispatcher';

import {
  WorkspaceLayoutExtensionDispatcher,
} from '../../core/workspace-sdk/runtime/workspace-layout-extension-dispatcher';

import {
  WorkspaceLayoutExtensionRegistry,
} from '../../core/workspace-sdk/runtime/workspace-layout-extension-registry';

import {
  WorkspaceLayoutFactory,
} from '../../core/workspace-sdk/runtime/workspace-layout-factory';

import {
  WorkspaceLayoutHookDispatcher,
} from '../../core/workspace-sdk/runtime/workspace-layout-hook-dispatcher';

import {
  WorkspaceLayoutHookRegistry,
} from '../../core/workspace-sdk/runtime/workspace-layout-hook-registry';

import {
  WorkspaceLayoutEngineRuntime,
} from '../../core/workspace-sdk/runtime/workspace-layout-engine-runtime';

import {
  WorkspaceLayoutObservability,
} from '../../core/workspace-sdk/runtime/workspace-layout-observability';

import {
  WorkspaceLayoutPersistence,
} from '../../core/workspace-sdk/runtime/workspace-layout-persistence';

import {
  WorkspaceLocalStorageLayoutStorage,
} from '../../core/workspace-sdk/runtime/workspace-local-storage-layout-storage';

import {
  WorkspaceRuntime,
} from '../../core/workspace-sdk/runtime/workspace-runtime';

/**
 * Composition Root oficial do Workspace.
 */
export class WorkspaceComposition {

  /**
   * Cria toda a infraestrutura institucional do Workspace.
   */
  static create(): WorkspaceRuntime {

    /**
     * Agregador único dos registries institucionais.
     */
    const registries =
      new WorkspaceRegistries();

    /**
     * Armazenamento institucional de referência utilizado
     * pelo Layout Engine e pela infraestrutura de persistência.
     */
    const layoutStorage =
      new WorkspaceLocalStorageLayoutStorage();

    /**
     * Layout Engine oficial associado aos mesmos registries
     * utilizados pelo Runtime.
     */
    const layoutEngine =
      new WorkspaceLayoutEngineRuntime(
        registries,
        layoutStorage,
      );

    /**
     * Infraestrutura institucional de persistência.
     */
    const layoutPersistence =
      new WorkspaceLayoutPersistence(
        layoutStorage,
      );

    /**
     * Infraestrutura institucional de eventos.
     */
    const layoutEvents =
      new WorkspaceLayoutEventDispatcher();

    /**
     * Registry e dispatcher institucionais de Hooks.
     */
    const layoutHookRegistry =
      new WorkspaceLayoutHookRegistry();

    const layoutHooks =
      new WorkspaceLayoutHookDispatcher(
        layoutHookRegistry,
      );

    /**
     * Registry e dispatcher institucionais de Extensions.
     */
    const layoutExtensionRegistry =
      new WorkspaceLayoutExtensionRegistry();

    const layoutExtensions =
      new WorkspaceLayoutExtensionDispatcher(
        layoutExtensionRegistry,
      );

    /**
     * Infraestrutura institucional de observabilidade.
     */
    const layoutObservability =
      new WorkspaceLayoutObservability();

    /**
     * Factory oficial do subsistema de Layout.
     */
    const layoutFactory =
      new WorkspaceLayoutFactory(
        layoutPersistence,
        layoutEvents,
        layoutHooks,
        layoutExtensions,
        layoutObservability,
      );

    /**
     * Instância única do Workspace Layout Manager.
     */
    const layoutManager =
      layoutFactory.create();

    /**
     * Workspace Editing API associada ao mesmo
     * Layout Manager utilizado pelo Runtime.
     */
    const editingFactory =
      new WorkspaceEditingFactory(
        layoutManager,
      );

    const editingManager =
      editingFactory.createManager();

    /**
     * Runtime oficial completamente composto.
     */
    return new WorkspaceRuntime(
      registries,
      undefined,
      undefined,
      undefined,
      layoutEngine,
      layoutManager,
      editingManager,
    );

  }

}