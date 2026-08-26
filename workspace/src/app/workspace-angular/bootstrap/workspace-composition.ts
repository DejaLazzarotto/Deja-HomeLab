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

import { WorkspaceClientManagementWidgetComponent } from '../components/workspace-client-management-widget/workspace-client-management-widget';

import { WorkspaceCompanyManagementWidgetComponent } from '../components/workspace-company-management-widget/workspace-company-management-widget';

import { WorkspaceIndicatorManagementWidgetComponent } from '../components/workspace-indicator-management-widget/workspace-indicator-management-widget';

import { WorkspaceMeasurementManagementWidgetComponent } from '../components/workspace-measurement-management-widget/workspace-measurement-management-widget';

import { WorkspaceOrganizationManagementWidgetComponent } from '../components/workspace-organization-management-widget/workspace-organization-management-widget';

import { WorkspaceUserManagementWidgetComponent } from '../components/workspace-user-management-widget/workspace-user-management-widget';

import { WorkspaceDashboardOverviewWidgetComponent } from '../components/workspace-dashboard-overview-widget/workspace-dashboard-overview-widget';

import { WorkspaceManagementReportWidgetComponent } from '../components/workspace-management-report-widget/workspace-management-report-widget';

/**
 * Composition Root oficial do Workspace.
 */
export class WorkspaceComposition {
  private static readonly CORE_OWNER = 'deja.workspace.core';

  private static readonly INITIAL_DASHBOARD_ID = 'deja.workspace.dashboard.initial';

  private static readonly ADMINISTRATION_DASHBOARD_ID = 'deja.workspace.dashboard.administration';

  private static readonly USERS_DASHBOARD_ID = 'deja.workspace.dashboard.administration.users';

  private static readonly PLATFORM_ORGANIZATIONS_DASHBOARD_ID =
    'deja.workspace.dashboard.platform.organizations';

  private static readonly REPORTS_DASHBOARD_ID = 'deja.workspace.dashboard.reports';

  private static readonly INDICATORS_DASHBOARD_ID = 'deja.workspace.dashboard.operation.indicators';

  private static readonly MEASUREMENTS_DASHBOARD_ID =
    'deja.workspace.dashboard.operation.measurements';

  private static readonly CLIENTS_DASHBOARD_ID = 'deja.workspace.dashboard.chamados.clients';

  private static readonly ACTIVITY_DASHBOARD_ID = 'deja.workspace.dashboard.activity';

  private static readonly TIMELINE_DASHBOARD_ID = 'deja.workspace.dashboard.timeline';

  private static readonly INITIAL_NAVIGATION_ID = 'deja.workspace.navigation.initial';

  private static readonly ADMINISTRATION_NAVIGATION_ID = 'deja.workspace.navigation.administration';

  private static readonly USERS_NAVIGATION_ID = 'deja.workspace.navigation.administration.users';

  private static readonly PLATFORM_ORGANIZATIONS_NAVIGATION_ID =
    'deja.workspace.navigation.platform.organizations';

  private static readonly REPORTS_NAVIGATION_ID = 'deja.workspace.navigation.reports';

  private static readonly INDICATORS_NAVIGATION_ID =
    'deja.workspace.navigation.operation.indicators';

  private static readonly MEASUREMENTS_NAVIGATION_ID =
    'deja.workspace.navigation.operation.measurements';

  private static readonly CLIENTS_NAVIGATION_ID = 'deja.workspace.navigation.chamados.clients';

  private static readonly ACTIVITY_NAVIGATION_ID = 'deja.workspace.navigation.activity';

  private static readonly TIMELINE_NAVIGATION_ID = 'deja.workspace.navigation.timeline';

  private static readonly INITIAL_LAYOUT_ID = 'deja.workspace.layout.initial';

  private static readonly MAIN_REGION_ID = 'deja.workspace.region.main';

  private static readonly WELCOME_WIDGET_ID = 'deja.workspace.widget.welcome';

  private static readonly DASHBOARD_OVERVIEW_WIDGET_ID = 'deja.workspace.widget.dashboard-overview';

  private static readonly COMPANY_MANAGEMENT_WIDGET_ID = 'deja.workspace.widget.company-management';

  private static readonly USER_MANAGEMENT_WIDGET_ID = 'deja.workspace.widget.user-management';

  private static readonly ORGANIZATION_MANAGEMENT_WIDGET_ID =
    'deja.workspace.widget.organization-management';

  private static readonly INDICATOR_MANAGEMENT_WIDGET_ID =
    'deja.workspace.widget.indicator-management';

  private static readonly MEASUREMENT_MANAGEMENT_WIDGET_ID =
    'deja.workspace.widget.measurement-management';

  private static readonly CLIENT_MANAGEMENT_WIDGET_ID = 'deja.workspace.widget.client-management';

  private static readonly MANAGEMENT_REPORT_WIDGET_ID = 'deja.workspace.widget.management-report';

  private static readonly INDICATORS_ACTION_ID = 'deja.workspace.widget.welcome.indicators';

  private static readonly ACTIVITY_ACTION_ID = 'deja.workspace.widget.welcome.activity';

  private static readonly TIMELINE_ACTION_ID = 'deja.workspace.widget.welcome.timeline';

  static create(): WorkspaceRuntime {
    const registries = new WorkspaceRegistries();

    this.registerInitialResources(registries);

    const layoutStorage = new WorkspaceLocalStorageLayoutStorage();

    const layoutEngine = new WorkspaceLayoutEngineRuntime(registries, layoutStorage);

    const layoutPersistence = new WorkspaceLayoutPersistence(layoutStorage);

    const layoutEvents = new WorkspaceLayoutEventDispatcher();

    const layoutHookRegistry = new WorkspaceLayoutHookRegistry();

    const layoutHooks = new WorkspaceLayoutHookDispatcher(layoutHookRegistry);

    const layoutExtensionRegistry = new WorkspaceLayoutExtensionRegistry();

    const layoutExtensions = new WorkspaceLayoutExtensionDispatcher(layoutExtensionRegistry);

    const layoutObservability = new WorkspaceLayoutObservability();

    const layoutFactory = new WorkspaceLayoutFactory(
      layoutPersistence,
      layoutEvents,
      layoutHooks,
      layoutExtensions,
      layoutObservability,
    );

    const layoutManager = layoutFactory.create();

    const editingFactory = new WorkspaceEditingFactory(layoutManager);

    const editingManager = editingFactory.createManager();

    const runtime = new WorkspaceRuntime(
      registries,
      undefined,
      undefined,
      undefined,
      layoutEngine,
      layoutManager,
      editingManager,
    );

    this.registerInitialActions(runtime);

    this.registerInitialNavigations(runtime);

    return runtime;
  }

  /**
   * Registra as Actions institucionais iniciais.
   */
  private static registerInitialActions(runtime: WorkspaceRuntime): void {
    runtime.registerActions([
      {
        id: this.INDICATORS_ACTION_ID,
        ownerId: this.CORE_OWNER,
        label: 'Indicadores',
        description: 'Acessa a gestão operacional de indicadores.',
        category: 'welcome',
        keywords: ['operação', 'indicadores', 'metas'],
        order: 10,
        visible: true,
        enabled: true,
        execute: async () => {
          await runtime.navigate(this.INDICATORS_NAVIGATION_ID);

          return {
            success: true,
            message: 'Indicadores abertos com sucesso.',
            completedAt: new Date(),
          };
        },
      },

      {
        id: this.ACTIVITY_ACTION_ID,
        ownerId: this.CORE_OWNER,
        label: 'Activity',
        description: 'Acessa eventos e atividades recentes do Workspace.',
        category: 'welcome',
        keywords: ['activity', 'eventos', 'atividades'],
        order: 20,
        visible: true,
        enabled: true,
        execute: async () => {
          await runtime.navigate(this.ACTIVITY_NAVIGATION_ID);

          return {
            success: true,
            message: 'Activity aberto com sucesso.',
            completedAt: new Date(),
          };
        },
      },

      {
        id: this.TIMELINE_ACTION_ID,
        ownerId: this.CORE_OWNER,
        label: 'Timeline',
        description: 'Acessa marcos e a evolução operacional do Workspace.',
        category: 'welcome',
        keywords: ['timeline', 'marcos', 'evolução'],
        order: 30,
        visible: true,
        enabled: true,
        execute: async () => {
          await runtime.navigate(this.TIMELINE_NAVIGATION_ID);

          return {
            success: true,
            message: 'Timeline aberta com sucesso.',
            completedAt: new Date(),
          };
        },
      },
    ]);
  }

  /**
   * Registra as navegações institucionais.
   */
  private static registerInitialNavigations(runtime: WorkspaceRuntime): void {
    runtime.registerNavigations([
      {
        id: this.INITIAL_NAVIGATION_ID,
        ownerId: this.CORE_OWNER,
        dashboardId: this.INITIAL_DASHBOARD_ID,
        title: 'Início',
        description: 'Abre o Dashboard inicial da Deja Platform.',
        icon: 'dashboard',
        order: 10,
        enabled: true,
        metadata: {
          section: 'home',
        },
      },

      {
        id: this.ADMINISTRATION_NAVIGATION_ID,
        ownerId: this.CORE_OWNER,
        dashboardId: this.ADMINISTRATION_DASHBOARD_ID,
        title: 'Empresas',
        description: 'Acesso à administração do Deja Indicadores.',
        icon: 'applications',
        order: 20,
        enabled: true,
        metadata: {
          section: 'administration',
        },
      },

      {
        id: this.USERS_NAVIGATION_ID,
        ownerId: this.CORE_OWNER,
        dashboardId: this.USERS_DASHBOARD_ID,
        title: 'Usuários',
        description: 'Acesso à administração de usuários e permissões.',
        icon: 'users',
        order: 25,
        enabled: true,
        metadata: {
          section: 'administration',
          permission: 'user-administration',
        },
      },

      {
        id: this.PLATFORM_ORGANIZATIONS_NAVIGATION_ID,
        ownerId: this.CORE_OWNER,
        dashboardId: this.PLATFORM_ORGANIZATIONS_DASHBOARD_ID,
        title: 'Organizações',
        description: 'Administração global de organizações e módulos.',
        icon: 'applications',
        order: 26,
        enabled: true,
        metadata: {
          section: 'administration',
          permission: 'platform-administration',
        },
      },

      {
        id: this.REPORTS_NAVIGATION_ID,
        ownerId: this.CORE_OWNER,
        dashboardId: this.REPORTS_DASHBOARD_ID,
        title: 'Relatórios',
        description: 'Acesso aos relatórios e análises dos indicadores.',
        icon: 'reports',
        order: 30,
        enabled: true,
        metadata: {
          section: 'analysis',
          moduleKey: 'reports',
        },
      },

      {
        id: this.INDICATORS_NAVIGATION_ID,
        ownerId: this.CORE_OWNER,
        dashboardId: this.INDICATORS_DASHBOARD_ID,
        title: 'Indicadores',
        description: 'Acesso à gestão operacional de indicadores.',
        icon: 'indicators',
        order: 30,
        enabled: true,
        metadata: {
          section: 'operation',
          moduleKey: 'indicators',
        },
      },

      {
        id: this.MEASUREMENTS_NAVIGATION_ID,
        ownerId: this.CORE_OWNER,
        dashboardId: this.MEASUREMENTS_DASHBOARD_ID,
        title: 'Coleta Manual',
        description: 'Acesso ao lançamento manual de medições.',
        icon: 'analytics',
        order: 40,
        enabled: true,
        metadata: {
          section: 'operation',
          moduleKey: 'measurements',
        },
      },

      {
        id: this.CLIENTS_NAVIGATION_ID,
        ownerId: this.CORE_OWNER,
        dashboardId: this.CLIENTS_DASHBOARD_ID,
        title: 'Clientes',
        description: 'Acesso à gestão de clientes do Deja Chamados.',
        icon: 'users',
        order: 10,
        enabled: true,
        metadata: {
          section: 'chamados',
          moduleKey: 'chamados',
        },
      },

      {
        id: this.ACTIVITY_NAVIGATION_ID,
        ownerId: this.CORE_OWNER,
        dashboardId: this.ACTIVITY_DASHBOARD_ID,
        title: 'Activity',
        description: 'Acesso aos eventos e atividades recentes do Workspace.',
        order: 50,
        enabled: true,
        visible: false,
        metadata: {
          section: 'operation',
        },
      },

      {
        id: this.TIMELINE_NAVIGATION_ID,
        ownerId: this.CORE_OWNER,
        dashboardId: this.TIMELINE_DASHBOARD_ID,
        title: 'Timeline',
        description: 'Acesso aos marcos e à evolução operacional do Workspace.',
        order: 60,
        enabled: true,
        visible: false,
        metadata: {
          section: 'analysis',
        },
      },
    ]);
  }

  private static registerInitialResources(registries: WorkspaceRegistries): void {
    const mainRegion: WorkspaceLayoutRegion = {
      id: this.MAIN_REGION_ID,
      owner: this.CORE_OWNER,
      title: 'Região principal',
      description: 'Região principal do Dashboard inicial do Workspace.',
      regionType: 'main',
      priority: 10,
      enabled: true,
      tags: ['core', 'initial', 'main'],
    };

    const initialLayout: WorkspaceLayout = {
      id: this.INITIAL_LAYOUT_ID,
      owner: this.CORE_OWNER,
      title: 'Layout inicial',
      description: 'Layout institucional utilizado pelos Dashboards iniciais.',
      type: 'grid',
      regionIds: [mainRegion.id],
      version: '1.0.0',
      priority: 10,
      enabled: true,
      tags: ['core', 'initial', 'dashboard'],
      configuration: {
        columns: 12,
        rowHeight: 'auto',
      },
    };

    const welcomeWidget: WorkspaceWidget = {
      id: this.WELCOME_WIDGET_ID,
      owner: this.CORE_OWNER,
      title: 'Bem-vindo à Deja Platform',
      description: 'Primeiro Widget institucional do Workspace.',
      category: 'system',
      widgetType: 'welcome',
      supportedSurfaces: ['dashboard'],
      capabilities: ['resizable', 'movable'],
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
      tags: ['core', 'initial', 'welcome'],
    };

    const dashboardOverviewWidget: WorkspaceWidget = {
      id: this.DASHBOARD_OVERVIEW_WIDGET_ID,
      owner: this.CORE_OWNER,
      title: 'Dashboard de Indicadores',
      description: 'Visão gerencial dos resultados e metas operacionais.',
      category: 'analysis',
      widgetType: 'dashboard-overview',
      supportedSurfaces: ['dashboard'],
      capabilities: ['resizable'],
      size: {
        default: {
          columns: 12,
          rows: 10,
        },
        minimum: {
          columns: 6,
          rows: 6,
        },
      },
      component: WorkspaceDashboardOverviewWidgetComponent,
      priority: 10,
      enabled: true,
      tags: ['deja-indicadores', 'dashboard', 'analysis'],
      metadata: {
        moduleKey: 'indicators',
      },
    };

    const companyManagementWidget: WorkspaceWidget = {
      id: this.COMPANY_MANAGEMENT_WIDGET_ID,
      owner: this.CORE_OWNER,
      title: 'Gestão de Empresas',
      description: 'Consulta e gerenciamento das empresas do Deja Indicadores.',
      category: 'management',
      widgetType: 'company-management',
      supportedSurfaces: ['dashboard'],
      capabilities: ['resizable'],
      size: {
        default: {
          columns: 12,
          rows: 8,
        },
        minimum: {
          columns: 6,
          rows: 4,
        },
      },
      component: WorkspaceCompanyManagementWidgetComponent,
      priority: 20,
      enabled: true,
      tags: ['deja-indicadores', 'companies', 'management'],
    };

    const userManagementWidget: WorkspaceWidget = {
      id: this.USER_MANAGEMENT_WIDGET_ID,
      owner: this.CORE_OWNER,
      title: 'Gestão de Usuários',
      description: 'Consulta e administração dos usuários institucionais.',
      category: 'management',
      widgetType: 'user-management',
      supportedSurfaces: ['dashboard'],
      capabilities: ['resizable'],
      size: {
        default: {
          columns: 12,
          rows: 8,
        },
        minimum: {
          columns: 6,
          rows: 4,
        },
      },
      component: WorkspaceUserManagementWidgetComponent,
      priority: 25,
      enabled: true,
      tags: ['deja-indicadores', 'users', 'management'],
    };

      const organizationManagementWidget: WorkspaceWidget = {
      id: this.ORGANIZATION_MANAGEMENT_WIDGET_ID,
      owner: this.CORE_OWNER,
      title: 'Gestão de Organizações',
      description: 'Administração global de organizações e módulos.',
      category: 'administration',
      widgetType: 'organization-management',
      supportedSurfaces: ['dashboard'],
      capabilities: ['resizable'],
      size: {
        default: {
          columns: 12,
          rows: 12,
        },
        minimum: {
          columns: 8,
          rows: 8,
        },
      },
      component: WorkspaceOrganizationManagementWidgetComponent,
      priority: 26,
      enabled: true,
      tags: ['platform', 'organizations', 'management'],
    };

    const indicatorManagementWidget: WorkspaceWidget = {
      id: this.INDICATOR_MANAGEMENT_WIDGET_ID,
      owner: this.CORE_OWNER,
      title: 'Gestão de Indicadores',
      description: 'Consulta e gerenciamento dos indicadores operacionais.',
      category: 'operation',
      widgetType: 'indicator-management',
      supportedSurfaces: ['dashboard'],
      capabilities: ['resizable'],
      size: {
        default: {
          columns: 12,
          rows: 8,
        },
        minimum: {
          columns: 6,
          rows: 4,
        },
      },
      component: WorkspaceIndicatorManagementWidgetComponent,
      priority: 30,
      enabled: true,
      tags: ['deja-indicadores', 'indicators', 'operation'],
      metadata: {
        moduleKey: 'indicators',
      },
    };

    const measurementManagementWidget: WorkspaceWidget = {
      id: this.MEASUREMENT_MANAGEMENT_WIDGET_ID,
      owner: this.CORE_OWNER,
      title: 'Coleta Manual',
      description: 'Consulta e lançamento manual de medições operacionais.',
      category: 'operation',
      widgetType: 'measurement-management',
      supportedSurfaces: ['dashboard'],
      capabilities: ['resizable'],
      size: {
        default: {
          columns: 12,
          rows: 8,
        },
        minimum: {
          columns: 6,
          rows: 4,
        },
      },
      component: WorkspaceMeasurementManagementWidgetComponent,
      priority: 40,
      enabled: true,
      tags: ['deja-indicadores', 'measurements', 'operation'],
      metadata: {
        moduleKey: 'measurements',
      },
    };

    const clientManagementWidget: WorkspaceWidget = {
      id: this.CLIENT_MANAGEMENT_WIDGET_ID,
      owner: this.CORE_OWNER,
      title: 'Gestão de Clientes',
      description: 'Consulta e gerenciamento dos clientes do Deja Chamados.',
      category: 'management',
      widgetType: 'client-management',
      supportedSurfaces: ['dashboard'],
      capabilities: ['resizable'],
      size: {
        default: {
          columns: 12,
          rows: 10,
        },
        minimum: {
          columns: 6,
          rows: 6,
        },
      },
      component: WorkspaceClientManagementWidgetComponent,
      priority: 40,
      enabled: true,
      tags: ['deja-chamados', 'clients', 'management'],
      metadata: {
        moduleKey: 'chamados',
      },
    };

    const managementReportWidget: WorkspaceWidget = {
      id: this.MANAGEMENT_REPORT_WIDGET_ID,
      owner: this.CORE_OWNER,
      title: 'Relatório Gerencial',
      description: 'Consulta gerencial dos indicadores e resultados.',
      category: 'analysis',
      widgetType: 'management-report',
      supportedSurfaces: ['dashboard'],
      capabilities: ['resizable'],
      size: {
        default: {
          columns: 12,
          rows: 10,
        },
        minimum: {
          columns: 6,
          rows: 6,
        },
      },
      component: WorkspaceManagementReportWidgetComponent,
      priority: 50,
      enabled: true,
      tags: ['deja-indicadores', 'reports', 'analysis'],
      metadata: {
        moduleKey: 'reports',
      },
    };

    registries.layoutRegions.register(mainRegion);

    registries.layouts.register(initialLayout);

    registries.widgets.register(welcomeWidget);

    registries.widgets.register(dashboardOverviewWidget);

    registries.widgets.register(companyManagementWidget);

    registries.widgets.register(userManagementWidget);

    registries.widgets.register(organizationManagementWidget);

    registries.widgets.register(indicatorManagementWidget);

    registries.widgets.register(measurementManagementWidget);

    registries.widgets.register(clientManagementWidget);

    registries.widgets.register(managementReportWidget);

    registries.dashboards.registerMany([
      {
        id: this.INITIAL_DASHBOARD_ID,
        owner: this.CORE_OWNER,
        title: 'Dashboard operacional',
        description: 'Visão gerencial dos indicadores e metas.',
        route: '/',
        layoutId: initialLayout.id,
        priority: 10,
        enabled: true,
        tags: ['deja-indicadores', 'dashboard', 'operation'],
        metadata: {
          type: 'dashboard',
          section: 'overview',
        },
        widgets: [
          {
            id: 'deja.workspace.widget-instance.dashboard-overview',
            widgetId: dashboardOverviewWidget.id,
            regionId: mainRegion.id,
            position: {
              column: 1,
              row: 1,
              columnSpan: 12,
              rowSpan: 10,
            },
            enabled: true,
          },
        ],
      },

      {
        id: this.ADMINISTRATION_DASHBOARD_ID,
        owner: this.CORE_OWNER,
        title: 'Administração',
        description: 'Gestão administrativa de empresas.',
        route: '/administration/companies',
        layoutId: initialLayout.id,
        priority: 20,
        enabled: true,
        tags: ['administration', 'companies'],
        metadata: {
          type: 'administration',
          section: 'companies',
        },
        widgets: [
          {
            id: 'deja.workspace.widget-instance.company-management',
            widgetId: companyManagementWidget.id,
            regionId: mainRegion.id,
            position: {
              column: 1,
              row: 1,
              columnSpan: 12,
              rowSpan: 8,
            },
            enabled: true,
          },
        ],
      },

      {
        id: this.USERS_DASHBOARD_ID,
        owner: this.CORE_OWNER,
        title: 'Usuários',
        description: 'Gestão administrativa de usuários e permissões.',
        route: '/administration/users',
        layoutId: initialLayout.id,
        priority: 25,
        enabled: true,
        tags: ['administration', 'users'],
        metadata: {
          type: 'administration',
          section: 'users',
          permission: 'user-administration',
        },
        widgets: [
          {
            id: 'deja.workspace.widget-instance.user-management',
            widgetId: userManagementWidget.id,
            regionId: mainRegion.id,
            position: {
              column: 1,
              row: 1,
              columnSpan: 12,
              rowSpan: 8,
            },
            enabled: true,
          },
        ],
      },

      {
        id: this.PLATFORM_ORGANIZATIONS_DASHBOARD_ID,
        owner: this.CORE_OWNER,
        title: 'Organizações',
        description: 'Administração global de organizações e módulos.',
        route: '/platform/organizations',
        layoutId: initialLayout.id,
        priority: 26,
        enabled: true,
        tags: ['platform', 'organizations', 'administration'],
        metadata: {
          type: 'platform-administration',
          section: 'organizations',
        },
        widgets: [
          {
            id: 'deja.workspace.widget-instance.organization-management',
            widgetId: organizationManagementWidget.id,
            regionId: mainRegion.id,
            position: {
              column: 1,
              row: 1,
              columnSpan: 12,
              rowSpan: 12,
            },
            enabled: true,
          },
        ],
      },

      {
        id: this.REPORTS_DASHBOARD_ID,
        owner: this.CORE_OWNER,
        title: 'Relatórios',
        description: 'Relatórios gerenciais dos indicadores.',
        route: '/reports',
        layoutId: initialLayout.id,
        priority: 30,
        enabled: true,
        tags: ['reports', 'analysis'],
        metadata: {
          type: 'reports',
          section: 'management',
          moduleKey: 'reports',
        },
        widgets: [
          {
            id: 'deja.workspace.widget-instance.management-report',
            widgetId: managementReportWidget.id,
            regionId: mainRegion.id,
            position: {
              column: 1,
              row: 1,
              columnSpan: 12,
              rowSpan: 10,
            },
            enabled: true,
          },
        ],
      },

      {
        id: this.INDICATORS_DASHBOARD_ID,
        owner: this.CORE_OWNER,
        title: 'Indicadores',
        description: 'Gestão operacional dos indicadores.',
        route: '/operation/indicators',
        layoutId: initialLayout.id,
        priority: 30,
        enabled: true,
        tags: ['operation', 'indicators'],
        metadata: {
          type: 'operation',
          section: 'indicators',
          moduleKey: 'indicators',
        },
        widgets: [
          {
            id: 'deja.workspace.widget-instance.indicator-management',
            widgetId: indicatorManagementWidget.id,
            regionId: mainRegion.id,
            position: {
              column: 1,
              row: 1,
              columnSpan: 12,
              rowSpan: 8,
            },
            enabled: true,
          },
        ],
      },

      {
        id: this.MEASUREMENTS_DASHBOARD_ID,
        owner: this.CORE_OWNER,
        title: 'Coleta Manual',
        description: 'Lançamento operacional de medições manuais.',
        route: '/operation/measurements',
        layoutId: initialLayout.id,
        priority: 40,
        enabled: true,
        tags: ['operation', 'measurements'],
        metadata: {
          type: 'operation',
          section: 'measurements',
          moduleKey: 'measurements',
        },
        widgets: [
          {
            id: 'deja.workspace.widget-instance.measurement-management',
            widgetId: measurementManagementWidget.id,
            regionId: mainRegion.id,
            position: {
              column: 1,
              row: 1,
              columnSpan: 12,
              rowSpan: 8,
            },
            enabled: true,
          },
        ],
      },

      {
        id: this.CLIENTS_DASHBOARD_ID,
        owner: this.CORE_OWNER,
        title: 'Clientes',
        description: 'Gestão de clientes atendidos pelo Deja Chamados.',
        route: '/chamados/clients',
        layoutId: initialLayout.id,
        priority: 40,
        enabled: true,
        tags: ['deja-chamados', 'clients', 'management'],
        metadata: {
          type: 'management',
          section: 'clients',
          moduleKey: 'chamados',
        },
        widgets: [
          {
            id: 'deja.workspace.widget-instance.client-management',
            widgetId: clientManagementWidget.id,
            regionId: mainRegion.id,
            position: {
              column: 1,
              row: 1,
              columnSpan: 12,
              rowSpan: 10,
            },
            enabled: true,
          },
        ],
      },

      {
        id: this.ACTIVITY_DASHBOARD_ID,
        owner: this.CORE_OWNER,
        title: 'Activity',
        description: 'Dashboard institucional de eventos e atividades recentes.',
        route: '/activity',
        layoutId: initialLayout.id,
        priority: 50,
        enabled: true,
        tags: ['activity'],
        metadata: {
          type: 'activity',
        },
      },

      {
        id: this.TIMELINE_DASHBOARD_ID,
        owner: this.CORE_OWNER,
        title: 'Timeline',
        description: 'Dashboard institucional de marcos e evolução operacional.',
        route: '/timeline',
        layoutId: initialLayout.id,
        priority: 60,
        enabled: true,
        tags: ['timeline'],
        metadata: {
          type: 'timeline',
        },
      },
    ]);
  }
}
