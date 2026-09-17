import { Routes } from '@angular/router';

import { administrationGuard } from './platform/authentication/application/administration.guard';
import { authenticationGuard } from './platform/authentication/application/authentication.guard';
import { platformAdministrationGuard } from './platform/authentication/application/platform-administration.guard';
import { portalAccessGuard } from './platform/authentication/application/portal-access.guard';
import { userAdministrationGuard } from './platform/authentication/application/user-administration.guard';
import { workspaceAccessGuard } from './platform/authentication/application/workspace-access.guard';
import { moduleGuard } from './platform/module-management/application/module.guard';

const workspacePage = () =>
  import('./workspace-angular/components/workspace-page/workspace-page').then(
    module => module.WorkspacePageComponent,
  );

export const routes: Routes = [
  {
    path: 'login',
    title: 'Entrar | Deja Platform',
    loadComponent: () =>
      import('./platform/authentication/presentation/login/login').then(
        module => module.LoginComponent,
      ),
  },
  {
    path: 'portal',
    canActivate: [
      authenticationGuard,
      portalAccessGuard,
    ],
    children: [
      {
        path: '',
        title: 'Portal do Cliente | Deja Chamados',
        loadComponent: () =>
          import(
            './deja-chamados/portal/presentation/portal-page/portal-page'
          ).then(
            module => module.PortalPageComponent,
          ),
      },
      {
        path: 'tickets/:id',
        title: 'Detalhes do chamado | Deja Chamados',
        loadComponent: () =>
          import(
            './deja-chamados/portal/presentation/portal-ticket-details/portal-ticket-details'
          ).then(
            module => module.PortalTicketDetailsComponent,
          ),
      },
    ],
  },
  {
    path: '',
    title: 'Deja Platform',
    canActivate: [
      authenticationGuard,
      workspaceAccessGuard,
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'platform/organizations',
    title: 'Organizações | Deja Platform',
    canActivate: [
      authenticationGuard,
      workspaceAccessGuard,
      platformAdministrationGuard,
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'administration',
    redirectTo: 'administration/companies',
    pathMatch: 'full',
  },
  {
    path: 'administration/companies',
    title: 'Empresas | Administração | Deja Indicadores',
    canActivate: [
      authenticationGuard,
      workspaceAccessGuard,
      administrationGuard,
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'administration/users',
    title: 'Usuários | Administração | Deja Platform',
    canActivate: [
      authenticationGuard,
      workspaceAccessGuard,
      userAdministrationGuard,
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'applications',
    redirectTo: 'administration/companies',
    pathMatch: 'full',
  },
  {
    path: 'operation',
    redirectTo: 'operation/indicators',
    pathMatch: 'full',
  },
  {
    path: 'operation/indicators',
    title: 'Indicadores | Operação | Deja Indicadores',
    canActivate: [
      authenticationGuard,
      workspaceAccessGuard,
      moduleGuard('indicators'),
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'operation/measurements',
    title: 'Coleta Manual | Operação | Deja Indicadores',
    canActivate: [
      authenticationGuard,
      workspaceAccessGuard,
      moduleGuard('measurements'),
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'chamados/tickets',
    title: 'Chamados | Deja Chamados',
    canActivate: [
      authenticationGuard,
      workspaceAccessGuard,
      moduleGuard('chamados'),
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'chamados/tickets/:id',
    title: 'Detalhes do chamado | Deja Chamados',
    canActivate: [
      authenticationGuard,
      workspaceAccessGuard,
      moduleGuard('chamados'),
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'chamados/queue',
    title: 'Fila | Deja Chamados',
    canActivate: [
      authenticationGuard,
      workspaceAccessGuard,
      moduleGuard('chamados'),
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'chamados/clients',
    title: 'Clientes | Deja Chamados',
    canActivate: [
      authenticationGuard,
      workspaceAccessGuard,
      moduleGuard('chamados'),
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'fotos',
    redirectTo: 'fotos/media',
    pathMatch: 'full',
  },
  {
    path: 'fotos/media',
    title: 'Album Admin | Deja Fotos',
    canActivate: [
      authenticationGuard,
      workspaceAccessGuard,
      moduleGuard('fotos'),
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'fotos/albums',
    title: 'Álbuns | Deja Fotos',
    canActivate: [
      authenticationGuard,
      workspaceAccessGuard,
      moduleGuard('fotos'),
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'analytics',
    redirectTo: 'operation/indicators',
    pathMatch: 'full',
  },
  {
    path: 'reports',
    title: 'Relatórios | Deja Indicadores',
    canActivate: [
      authenticationGuard,
      workspaceAccessGuard,
      moduleGuard('reports'),
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'activity',
    title: 'Atividades | Deja Platform',
    canActivate: [
      authenticationGuard,
      workspaceAccessGuard,
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'timeline',
    title: 'Linha do tempo | Deja Platform',
    canActivate: [
      authenticationGuard,
      workspaceAccessGuard,
    ],
    loadComponent: workspacePage,
  },
  {
    path: '**',
    redirectTo: '',
  },
];
