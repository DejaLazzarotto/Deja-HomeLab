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
  UserRole,
} from '../domain/authenticated-user';

import {
  AuthenticationService,
} from './authentication.service';

export const userAdministrationRoles: readonly UserRole[] = [
  'platform_admin',
  'organization_admin',
  'tenant_admin',
];

export const canAccessUserAdministration = (
  role: UserRole,
): boolean => userAdministrationRoles.includes(role);

export const userAdministrationGuard: CanActivateFn = () => {
  const authentication = inject(AuthenticationService);
  const router = inject(Router);

  const authorize = (
    role: UserRole,
  ): true | ReturnType<Router['createUrlTree']> => (
    canAccessUserAdministration(role)
      ? true
      : router.createUrlTree([
          '/',
        ])
  );

  const currentUser = authentication.user();

  if (currentUser) {
    return authorize(currentUser.role);
  }

  if (!authentication.getAccessToken()) {
    return router.createUrlTree([
      '/login',
    ]);
  }

  return authentication.restoreSession().pipe(
    map(user => (
      user
        ? authorize(user.role)
        : router.createUrlTree([
            '/login',
          ])
    )),
  );
};