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
    path: 'dates/:year/:month',
    title: 'Período | Fotos',
    canActivate: [
      fotosAccessGuard,
    ],
    loadComponent: () =>
      import(
        './features/dates/month-page/month-page'
      ).then(
        module => module.MonthPageComponent,
      ),
  },
  {
    path: 'dates/:year',
    title: 'Ano | Fotos',
    canActivate: [
      fotosAccessGuard,
    ],
    loadComponent: () =>
      import(
        './features/dates/year-page/year-page'
      ).then(
        module => module.YearPageComponent,
      ),
  },
  {
    path: 'dates',
    title: 'Por datas | Fotos',
    canActivate: [
      fotosAccessGuard,
    ],
    loadComponent: () =>
      import(
        './features/dates/dates-page/dates-page'
      ).then(
        module => module.DatesPageComponent,
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