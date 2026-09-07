import { Routes } from '@angular/router';

import { administrationGuard } from './platform/authentication/application/administration.guard';

import { authenticationGuard } from './platform/authentication/application/authentication.guard';

import { platformAdministrationGuard } from './platform/authentication/application/platform-administration.guard';

import { userAdministrationGuard } from './platform/authentication/application/user-administration.guard';

import { moduleGuard } from './platform/module-management/application/module.guard';

const workspacePage = () =>
  import('./workspace-angular/components/workspace-page/workspace-page').then(
    (module) => module.WorkspacePageComponent,
  );

export const routes: Routes = [
  {
    path: 'login',
    title: 'Entrar | Deja Platform',
    loadComponent: () =>
      import('./platform/authentication/presentation/login/login').then(
        (module) => module.LoginComponent,
      ),
  },
  {
    path: '',
    title: 'Deja Platform',
    canActivate: [authenticationGuard],
    loadComponent: workspacePage,
  },
  {
    path: 'platform/organizations',
    title: 'Organizações | Deja Platform',
    canActivate: [authenticationGuard, platformAdministrationGuard],
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
    canActivate: [administrationGuard],
    loadComponent: workspacePage,
  },
  {
    path: 'administration/users',
    title: 'Usuários | Administração | Deja Platform',
    canActivate: [userAdministrationGuard],
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
    canActivate: [authenticationGuard, moduleGuard('indicators')],
    loadComponent: workspacePage,
  },
  {
    path: 'operation/measurements',
    title: 'Coleta Manual | Operação | Deja Indicadores',
    canActivate: [authenticationGuard, moduleGuard('measurements')],
    loadComponent: workspacePage,
  },
  {
    path: 'chamados/tickets',
    title: 'Chamados | Deja Chamados',
    canActivate: [authenticationGuard, moduleGuard('chamados')],
    loadComponent: workspacePage,
  },
  {
    path: 'chamados/queue',
    title: 'Fila | Deja Chamados',
    canActivate: [authenticationGuard, moduleGuard('chamados')],
    loadComponent: workspacePage,
  },
  {
    path: 'chamados/clients',
    title: 'Clientes | Deja Chamados',
    canActivate: [authenticationGuard, moduleGuard('chamados')],
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
    canActivate: [authenticationGuard, moduleGuard('reports')],
    loadComponent: workspacePage,
  },
  {
    path: 'activity',
    title: 'Atividades | Deja Platform',
    canActivate: [authenticationGuard],
    loadComponent: workspacePage,
  },
  {
    path: 'timeline',
    title: 'Linha do tempo | Deja Platform',
    canActivate: [authenticationGuard],
    loadComponent: workspacePage,
  },
  {
    path: '**',
    redirectTo: '',
  },
];
