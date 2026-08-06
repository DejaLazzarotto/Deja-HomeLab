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

import { WorkspaceRegistries } from '../../core/workspace-sdk/registries/workspace-registries';

import { WorkspaceDashboard } from '../../core/workspace-sdk/runtime/workspace-dashboard';

import { WorkspaceEditingFactory } from '../../core/workspace-sdk/runtime/workspace-editing-factory';

import { WorkspaceLayout } from '../../core/workspace-sdk/runtime/workspace-layout';

import { WorkspaceLayoutEventDispatcher } from '../../core/workspace-sdk/runtime/workspace-layout-event-dispatcher';

import { WorkspaceLayoutExtensionDispatcher } from '../../core/workspace-sdk/runtime/workspace-layout-extension-dispatcher';

import { WorkspaceLayoutExtensionRegistry } from '../../core/workspace-sdk/runtime/workspace-layout-extension-registry';

import { WorkspaceLayoutFactory } from '../../core/workspace-sdk/runtime/workspace-layout-factory';

import { WorkspaceLayoutHookDispatcher } from '../../core/workspace-sdk/runtime/workspace-layout-hook-dispatcher';

import { WorkspaceLayoutHookRegistry } from '../../core/workspace-sdk/runtime/workspace-layout-hook-registry';

import { WorkspaceLayoutEngineRuntime } from '../../core/workspace-sdk/runtime/workspace-layout-engine-runtime';

import { WorkspaceLayoutObservability } from '../../core/workspace-sdk/runtime/workspace-layout-observability';

import { WorkspaceLayoutPersistence } from '../../core/workspace-sdk/runtime/workspace-layout-persistence';

import { WorkspaceLayoutRegion } from '../../core/workspace-sdk/runtime/workspace-layout-region';

import { WorkspaceLocalStorageLayoutStorage } from '../../core/workspace-sdk/runtime/workspace-local-storage-layout-storage';

import { WorkspaceNavigation } from '../../core/workspace-sdk/runtime/workspace-navigation';

import { WorkspaceRuntime } from '../../core/workspace-sdk/runtime/workspace-runtime';

import { WorkspaceWidget } from '../../core/workspace-sdk/runtime/workspace-widget';

import { WorkspaceWelcomeWidgetComponent } from '../components/workspace-welcome-widget/workspace-welcome-widget';

/**
 * Composition Root oficial do Workspace.
 */
export class WorkspaceComposition {
  /**
   * Proprietário institucional dos recursos iniciais.
   */
  private static readonly CORE_OWNER = 'deja.workspace.core';

  /**
   * Identificadores dos recursos institucionais iniciais.
   */
  private static readonly INITIAL_DASHBOARD_ID =
    'deja.workspace.dashboard.initial';

  private static readonly INITIAL_NAVIGATION_ID =
    'deja.workspace.navigation.initial';

  private static readonly INITIAL_LAYOUT_ID =
    'deja.workspace.layout.initial';

  private static readonly MAIN_REGION_ID =
    'deja.workspace.region.main';

  private static readonly WELCOME_WIDGET_ID =
    'deja.workspace.widget.welcome';

  /**
   * Cria toda a infraestrutura institucional do Workspace.
   */
  static create(): WorkspaceRuntime {
    /**
     * Agregador único dos registries institucionais.
     */
    const registries = new WorkspaceRegistries();

    /**
     * Registra os primeiros recursos institucionais
     * disponibilizados pelo Workspace.
     */
    this.registerInitialResources(registries);

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
    const runtime = new WorkspaceRuntime(
      registries,
      undefined,
      undefined,
      undefined,
      layoutEngine,
      layoutManager,
      editingManager,
    );

    this.registerInitialNavigation(runtime);

    return runtime;
  }

  /**
   * Registra a navegação institucional inicial.
   */
  private static registerInitialNavigation(
    runtime: WorkspaceRuntime,
  ): void {
    const initialNavigation: WorkspaceNavigation = {
      id: this.INITIAL_NAVIGATION_ID,
      ownerId: this.CORE_OWNER,
      dashboardId: this.INITIAL_DASHBOARD_ID,
      title: 'Início',
      description:
        'Abre o Dashboard inicial da Deja Platform.',
      icon: 'home',
      order: 10,
      enabled: true,
      metadata: {
        route: '/',
      },
    };

    runtime.registerNavigation(
      initialNavigation,
    );
  }

  /**
   * Registra os recursos institucionais iniciais do Workspace.
   */
  private static registerInitialResources(
    registries: WorkspaceRegistries,
  ): void {
    const mainRegion: WorkspaceLayoutRegion = {
      id: this.MAIN_REGION_ID,
      owner: this.CORE_OWNER,
      title: 'Região principal',
      description:
        'Região principal do Dashboard inicial do Workspace.',
      regionType: 'main',
      priority: 10,
      enabled: true,
      tags: [
        'core',
        'initial',
        'main',
      ],
    };

    const initialLayout: WorkspaceLayout = {
      id: this.INITIAL_LAYOUT_ID,
      owner: this.CORE_OWNER,
      title: 'Layout inicial',
      description:
        'Layout institucional utilizado pelo Dashboard inicial.',
      type: 'grid',
      regionIds: [
        mainRegion.id,
      ],
      version: '1.0.0',
      priority: 10,
      enabled: true,
      tags: [
        'core',
        'initial',
        'dashboard',
      ],
      configuration: {
        columns: 12,
        rowHeight: 'auto',
      },
    };

    const welcomeWidget: WorkspaceWidget = {
      id: this.WELCOME_WIDGET_ID,
      owner: this.CORE_OWNER,
      title: 'Bem-vindo à Deja Platform',
      description:
        'Primeiro Widget institucional do Workspace.',
      category: 'system',
      widgetType: 'welcome',
      supportedSurfaces: [
        'dashboard',
      ],
      capabilities: [
        'resizable',
        'movable',
      ],
      size: {
        default: {
          columns: 12,
          rows: 4,
        },
        minimum: {
          columns: 4,
          rows: 2,
        },
      },
      component: WorkspaceWelcomeWidgetComponent,
      priority: 10,
      enabled: true,
      tags: [
        'core',
        'initial',
        'welcome',
      ],
      defaultConfiguration: {
        message:
          'A infraestrutura inicial da Deja Platform está funcionando.',
      },
    };

    const initialDashboard: WorkspaceDashboard = {
      id: this.INITIAL_DASHBOARD_ID,
      owner: this.CORE_OWNER,
      title: 'Dashboard inicial',
      description:
        'Primeiro Dashboard institucional da Deja Platform.',
      route: '/',
      layoutId: initialLayout.id,
      priority: 10,
      enabled: true,
      tags: [
        'core',
        'initial',
        'default',
      ],
      widgets: [
        {
          id:
            'deja.workspace.widget-instance.welcome',
          widgetId: welcomeWidget.id,
          regionId: mainRegion.id,
          position: {
            column: 1,
            row: 1,
            columnSpan: 12,
            rowSpan: 4,
          },
          enabled: true,
        },
      ],
    };

    registries.layoutRegions.register(
      mainRegion,
    );

    registries.layouts.register(
      initialLayout,
    );

    registries.widgets.register(
      welcomeWidget,
    );

    registries.dashboards.register(
      initialDashboard,
    );
  }
}
