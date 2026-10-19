import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { WelcomeService } from './welcome.service';

export const welcomeEntryGuard: CanActivateFn = () => {
  const router = inject(Router);
  const welcome = inject(WelcomeService);

  return router.createUrlTree([
    welcome.shouldShow() ? '/welcome' : '/explore',
  ]);
};
