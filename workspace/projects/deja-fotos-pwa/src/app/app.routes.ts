import {
  Routes,
} from '@angular/router';

import {
  fotosAccessGuard,
} from './core/authentication/fotos-access.guard';

export const routes: Routes = [
  {
    path: 'login',
    title: 'Entrar | Fotos',
    loadComponent: () =>
      import(
        './features/authentication/login/login'
      ).then(
        module => module.LoginComponent,
      ),
  },
  {
    path: 'explore',
    title: 'Explorar | Fotos',
    canActivate: [
      fotosAccessGuard,
    ],
    loadComponent: () =>
      import(
        './features/explore/explore-page/explore-page'
      ).then(
        module => module.ExplorePageComponent,
      ),
  },
  {
    path: 'albums',
    title: 'Meus álbuns | Fotos',
    canActivate: [
      fotosAccessGuard,
    ],
    loadComponent: () =>
      import(
        './features/albums/albums-page/albums-page'
      ).then(
        module => module.AlbumsPageComponent,
      ),
  },
  {
    path: '',
    redirectTo: 'explore',
    pathMatch: 'full',
  },
  {
    path: '**',
    redirectTo: 'explore',
  },
];