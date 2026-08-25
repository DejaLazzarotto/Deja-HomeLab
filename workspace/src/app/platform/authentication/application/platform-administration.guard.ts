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

export const platformAdministrationGuard: CanActivateFn = () => {
  const authentication = inject(AuthenticationService);
  const router = inject(Router);

  const authorize = (
    role: string,
  ): true | ReturnType<Router['createUrlTree']> => (
    role === 'platform_admin'
      ? true
      : router.createUrlTree(['/'])
  );

  const currentUser = authentication.user();

  if (currentUser) {
    return authorize(currentUser.role);
  }

  if (!authentication.getAccessToken()) {
    return router.createUrlTree(['/login']);
  }

  return authentication.restoreSession().pipe(
    map(user => (
      user
        ? authorize(user.role)
        : router.createUrlTree(['/login'])
    )),
  );
};