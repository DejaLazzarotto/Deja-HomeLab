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
} from '../../authentication/application/authentication.service';

import {
  ModuleKey,
} from '../domain/module-key';

import {
  canAccessModule,
} from './module-access';

export const moduleGuard = (
  moduleKey: ModuleKey,
): CanActivateFn => () => {
  const authentication = inject(AuthenticationService);
  const router = inject(Router);

  const authorize = (
    user: ReturnType<AuthenticationService['user']>,
  ): true | ReturnType<Router['createUrlTree']> => (
    canAccessModule(user, moduleKey)
      ? true
      : router.createUrlTree([
          '/',
        ])
  );

  const currentUser = authentication.user();

  if (currentUser) {
    return authorize(currentUser);
  }

  if (!authentication.getAccessToken()) {
    return router.createUrlTree([
      '/login',
    ]);
  }

  return authentication.restoreSession().pipe(
    map(user => (
      user
        ? authorize(user)
        : router.createUrlTree([
            '/login',
          ])
    )),
  );
};