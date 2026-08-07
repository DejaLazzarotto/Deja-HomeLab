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

  private static readonly CORE_OWNER =
    'deja.workspace.core';


  private static readonly INITIAL_DASHBOARD_ID =
    'deja.workspace.dashboard.initial';

  private static readonly APPLICATIONS_DASHBOARD_ID =
    'deja.workspace.dashboard.applications';

  private static readonly REPORTS_DASHBOARD_ID =
    'deja.workspace.dashboard.reports';


  private static readonly INITIAL_NAVIGATION_ID =
    'deja.workspace.navigation.initial';

  private static readonly APPLICATIONS_NAVIGATION_ID =
    'deja.workspace.navigation.applications';

  private static readonly REPORTS_NAVIGATION_ID =
    'deja.workspace.navigation.reports';


  private static readonly INITIAL_LAYOUT_ID =
    'deja.workspace.layout.initial';


  private static readonly MAIN_REGION_ID =
    'deja.workspace.region.main';


  private static readonly WELCOME_WIDGET_ID =
    'deja.workspace.widget.welcome';


  static create(): WorkspaceRuntime {

    const registries =
      new WorkspaceRegistries();


    this.registerInitialResources(
      registries,
    );


    const layoutStorage =
      new WorkspaceLocalStorageLayoutStorage();


    const layoutEngine =
      new WorkspaceLayoutEngineRuntime(
        registries,
        layoutStorage,
      );


    const layoutPersistence =
      new WorkspaceLayoutPersistence(
        layoutStorage,
      );


    const layoutEvents =
      new WorkspaceLayoutEventDispatcher();


    const layoutHookRegistry =
      new WorkspaceLayoutHookRegistry();


    const layoutHooks =
      new WorkspaceLayoutHookDispatcher(
        layoutHookRegistry,
      );


    const layoutExtensionRegistry =
      new WorkspaceLayoutExtensionRegistry();


    const layoutExtensions =
      new WorkspaceLayoutExtensionDispatcher(
        layoutExtensionRegistry,
      );


    const layoutObservability =
      new WorkspaceLayoutObservability();


    const layoutFactory =
      new WorkspaceLayoutFactory(
        layoutPersistence,
        layoutEvents,
        layoutHooks,
        layoutExtensions,
        layoutObservability,
      );


    const layoutManager =
      layoutFactory.create();


    const editingFactory =
      new WorkspaceEditingFactory(
        layoutManager,
      );


    const editingManager =
      editingFactory.createManager();


    const runtime =
      new WorkspaceRuntime(
        registries,
        undefined,
        undefined,
        undefined,
        layoutEngine,
        layoutManager,
        editingManager,
      );


    this.registerInitialNavigations(
      runtime,
    );


    return runtime;

  }


  /**
   * Registra as navegações institucionais.
   */
  private static registerInitialNavigations(
    runtime: WorkspaceRuntime,
  ): void {

    runtime.registerNavigations([

      {
        id: this.INITIAL_NAVIGATION_ID,
        ownerId: this.CORE_OWNER,
        dashboardId: this.INITIAL_DASHBOARD_ID,
        title: 'Início',
        description:
          'Abre o Dashboard inicial da Deja Platform.',
        icon: 'dashboard',
        order: 10,
        enabled: true,
      },

      {
        id: this.APPLICATIONS_NAVIGATION_ID,
        ownerId: this.CORE_OWNER,
        dashboardId: this.APPLICATIONS_DASHBOARD_ID,
        title: 'Applications',
        description:
          'Acesso às aplicações da plataforma.',
        icon: 'applications',
        order: 20,
        enabled: true,
      },

      {
        id: this.REPORTS_NAVIGATION_ID,
        ownerId: this.CORE_OWNER,
        dashboardId: this.REPORTS_DASHBOARD_ID,
        title: 'Reports',
        description:
          'Acesso aos relatórios da plataforma.',
        icon: 'reports',
        order: 30,
        enabled: true,
      },

    ]);

  }


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
        'Layout institucional utilizado pelos Dashboards iniciais.',
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


    registries.dashboards.registerMany([

      {
        id: this.INITIAL_DASHBOARD_ID,
        owner: this.CORE_OWNER,
        title: 'Dashboard inicial',
        description:
          'Primeiro Dashboard institucional.',
        route: '/',
        layoutId: initialLayout.id,
        priority: 10,
        enabled: true,
        tags: [
          'core',
          'initial',
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
      },


      {
        id: this.APPLICATIONS_DASHBOARD_ID,
        owner: this.CORE_OWNER,
        title: 'Applications',
        description:
          'Dashboard institucional de aplicações.',
        route: '/applications',
        layoutId: initialLayout.id,
        priority: 20,
        enabled: true,
        tags: [
          'applications',
        ],
        metadata: {
          type: 'applications',
        },
      },


      {
        id: this.REPORTS_DASHBOARD_ID,
        owner: this.CORE_OWNER,
        title: 'Reports',
        description:
          'Dashboard institucional de relatórios.',
        route: '/reports',
        layoutId: initialLayout.id,
        priority: 30,
        enabled: true,
        tags: [
          'reports',
        ],
        metadata: {
          type: 'reports',
        },
      },

    ]);

  }

}
