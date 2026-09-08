import {
  inject,
} from '@angular/core';

import {
  CanActivateFn,
  Router,
} from '@angular/router';

import {
  map,
  of,
  switchMap,
} from 'rxjs';

import {
  AuthenticationService,
} from './authentication.service';

export const workspaceAccessGuard: CanActivateFn = () => {
  const authentication = inject(AuthenticationService);
  const router = inject(Router);

  const currentUser = authentication.user();

  if (currentUser) {
    return currentUser.role === 'client'
      ? router.parseUrl('/portal')
      : true;
  }

  if (!authentication.getAccessToken()) {
    return router.parseUrl('/login');
  }

  return of(null).pipe(
    switchMap(() => authentication.restoreSession()),
    map(user => {
      if (!user) {
        return router.parseUrl('/login');
      }

      if (user.role === 'client') {
        return router.parseUrl('/portal');
      }

      return true;
    }),
  );
};