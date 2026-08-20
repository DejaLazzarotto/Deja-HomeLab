import { Routes } from '@angular/router';

import { administrationGuard } from './deja-indicadores/authentication/application/administration.guard';

import { authenticationGuard } from './deja-indicadores/authentication/application/authentication.guard';

const workspacePage = () =>
  import('./workspace-angular/components/workspace-page/workspace-page').then(
    (module) => module.WorkspacePageComponent,
  );

export const routes: Routes = [
  {
    path: 'login',
    title: 'Entrar | Deja Indicadores',
    loadComponent: () =>
      import('./deja-indicadores/authentication/presentation/login/login').then(
        (module) => module.LoginComponent,
      ),
  },
  {
    path: '',
    title: 'Deja Indicadores',
    canActivate: [authenticationGuard],
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
    canActivate: [authenticationGuard],
    loadComponent: workspacePage,
  },
  {
    path: 'operation/measurements',
    title: 'Coleta Manual | Operação | Deja Indicadores',
    canActivate: [authenticationGuard],
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
    canActivate: [authenticationGuard],
    loadComponent: workspacePage,
  },
  {
    path: 'activity',
    title: 'Atividades | Deja Indicadores',
    canActivate: [authenticationGuard],
    loadComponent: workspacePage,
  },
  {
    path: 'timeline',
    title: 'Linha do tempo | Deja Indicadores',
    canActivate: [authenticationGuard],
    loadComponent: workspacePage,
  },
  {
    path: '**',
    redirectTo: '',
  },
];
