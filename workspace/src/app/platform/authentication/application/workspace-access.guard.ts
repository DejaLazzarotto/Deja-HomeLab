import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { map } from 'rxjs';

import { AuthenticationService } from './authentication.service';
import { canAccessWorkspace } from './workspace-access-policy';

export const workspaceAccessGuard: CanActivateFn = () => {
  const authentication = inject(AuthenticationService);
  const router = inject(Router);

  const authorize = (
    user: ReturnType<AuthenticationService['user']>,
  ) => {
    if (!user) {
      return router.parseUrl('/login');
    }

    if (user.role === 'client') {
      return router.parseUrl('/portal');
    }

    return canAccessWorkspace(user)
      ? true
      : router.parseUrl('/login');
  };

  const currentUser = authentication.user();

  if (currentUser) {
    return authorize(currentUser);
  }

  if (!authentication.getAccessToken()) {
    return router.parseUrl('/login');
  }

  return authentication.restoreSession().pipe(
    map(user => authorize(user)),
  );
};
