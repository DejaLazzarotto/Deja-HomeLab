import {
  Routes,
} from '@angular/router';

import {
  authenticationGuard,
} from './deja-indicadores/authentication/application/authentication.guard';

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
    loadComponent: () => import(
      './workspace-angular/components/workspace-page/workspace-page'
    ).then(module => module.WorkspacePageComponent),
  },
  {
    path: '**',
    redirectTo: '',
  },
];
