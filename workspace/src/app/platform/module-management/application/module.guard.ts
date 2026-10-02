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

import type {
  UserModuleRole,
} from '../../authentication/domain/authenticated-user';

import {
  ModuleKey,
} from '../domain/module-key';

import {
  canAccessModule,
  getModuleRole,
} from './module-access';

export const moduleGuard = (
  moduleKey: ModuleKey,
  allowedRoles?: readonly UserModuleRole[],
): CanActivateFn => () => {
  const authentication = inject(AuthenticationService);
  const router = inject(Router);

  const authorize = (
    user: ReturnType<AuthenticationService['user']>,
  ): true | ReturnType<Router['createUrlTree']> => {
    if (!canAccessModule(user, moduleKey)) {
      return router.createUrlTree([
        '/',
      ]);
    }

    if (
      user?.role === 'platform_admin'
      || !allowedRoles?.length
    ) {
      return true;
    }

    const moduleRole = getModuleRole(
      user,
      moduleKey,
    );

    return (
      moduleRole
      && allowedRoles.includes(moduleRole)
    )
      ? true
      : router.createUrlTree([
          '/',
        ]);
  };

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