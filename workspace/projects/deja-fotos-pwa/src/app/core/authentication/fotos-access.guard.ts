import {
  inject,
} from '@angular/core';

import {
  CanActivateFn,
  Router,
} from '@angular/router';

import {
  map,
} from 'rxjs';

import {
  AuthenticationService,
} from './authentication.service';

export const fotosAccessGuard: CanActivateFn = () => {
  const authentication =
    inject(AuthenticationService);

  const router =
    inject(Router);

  const authorize = (): true | ReturnType<Router['createUrlTree']> => {
    return authentication.canAccessFotos()
      ? true
      : router.createUrlTree([
          '/login',
        ]);
  };

  if (authentication.isAuthenticated()) {
    return authorize();
  }

  if (!authentication.getAccessToken()) {
    return router.createUrlTree([
      '/login',
    ]);
  }

  return authentication.restoreSession().pipe(
    map(user => (
      user
        ? authorize()
        : router.createUrlTree([
            '/login',
          ])
    )),
  );
};