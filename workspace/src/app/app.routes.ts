import {
  Routes,
} from '@angular/router';

import {
  authenticationGuard,
} from './deja-indicadores/authentication/application/authentication.guard';

const workspacePage = () => import(
  './workspace-angular/components/workspace-page/workspace-page'
).then(module => module.WorkspacePageComponent);

export const routes: Routes = [
  {
    path: 'login',
    title: 'Entrar | Deja Indicadores',
    loadComponent: () => import(
      './deja-indicadores/authentication/presentation/login/login'
    ).then(module => module.LoginComponent),
  },
  {
    path: '',
    title: 'Deja Indicadores',
    canActivate: [
      authenticationGuard,
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'applications',
    title: 'Empresas | Deja Indicadores',
    canActivate: [
      authenticationGuard,
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'reports',
    title: 'Relatórios | Deja Indicadores',
    canActivate: [
      authenticationGuard,
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'analytics',
    title: 'Indicadores | Deja Indicadores',
    canActivate: [
      authenticationGuard,
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'activity',
    title: 'Atividades | Deja Indicadores',
    canActivate: [
      authenticationGuard,
    ],
    loadComponent: workspacePage,
  },
  {
    path: 'timeline',
    title: 'Linha do tempo | Deja Indicadores',
    canActivate: [
      authenticationGuard,
    ],
    loadComponent: workspacePage,
  },
  {
    path: '**',
    redirectTo: '',
  },
];
