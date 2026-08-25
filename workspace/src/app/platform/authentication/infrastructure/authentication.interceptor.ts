import {
  inject,
} from '@angular/core';

import {
  HttpInterceptorFn,
} from '@angular/common/http';

import {
  AuthenticationService,
} from '../application/authentication.service';

export const authenticationInterceptor: HttpInterceptorFn = (
  request,
  next,
) => {
  const authentication = inject(AuthenticationService);
  const accessToken = authentication.getAccessToken();

  if (
    !accessToken
    || request.url.endsWith('/api/v1/auth/login')
  ) {
    return next(request);
  }

  return next(
    request.clone({
      setHeaders: {
        Authorization: `Bearer ${accessToken}`,
      },
    }),
  );
};