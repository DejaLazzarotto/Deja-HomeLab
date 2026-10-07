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
    path: 'people/:personId/media/:mediaId',
    title: 'Visualizar mídia | Fotos',
    canActivate: [
      fotosAccessGuard,
    ],
    loadComponent: () =>
      import(
        './features/people/person-media-viewer-page/person-media-viewer-page'
      ).then(
        module => module.PersonMediaViewerPageComponent,
      ),
  },
  {
    path: 'people/:personId',
    title: 'Mídias da pessoa | Fotos',
    canActivate: [
      fotosAccessGuard,
    ],
    loadComponent: () =>
      import(
        './features/people/person-media-page/person-media-page'
      ).then(
        module => module.PersonMediaPageComponent,
      ),
  },
  {
    path: 'people',
    title: 'Por pessoas | Fotos',
    canActivate: [
      fotosAccessGuard,
    ],
    loadComponent: () =>
      import(
        './features/people/people-page/people-page'
      ).then(
        module => module.PeoplePageComponent,
      ),
  },
  {
    path: 'dates/:year/:month/media/:mediaId',
    title: 'Visualizar mídia | Fotos',
    canActivate: [
      fotosAccessGuard,
    ],
    loadComponent: () =>
      import(
        './features/dates/media-viewer-page/media-viewer-page'
      ).then(
        module => module.MediaViewerPageComponent,
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