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

export const authenticationGuard: CanActivateFn = () => {
  const authentication = inject(AuthenticationService);
  const router = inject(Router);

  if (authentication.isAuthenticated()) {
    return true;
  }

  if (!authentication.getAccessToken()) {
    return router.createUrlTree([
      '/login',
    ]);
  }

  return authentication.restoreSession().pipe(
    map(user => (
      user
        ? true
        : router.createUrlTree([
            '/login',
          ])
    )),
  );
};