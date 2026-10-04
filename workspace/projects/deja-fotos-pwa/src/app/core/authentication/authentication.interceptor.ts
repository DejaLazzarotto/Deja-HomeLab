import {
  inject,
} from '@angular/core';

import {
  HttpErrorResponse,
  HttpInterceptorFn,
} from '@angular/common/http';

import {
  Router,
} from '@angular/router';

import {
  catchError,
  throwError,
} from 'rxjs';

import {
  AuthenticationService,
} from './authentication.service';

export const authenticationInterceptor: HttpInterceptorFn = (
  request,
  next,
) => {
  const authentication =
    inject(AuthenticationService);

  const router =
    inject(Router);

  const accessToken =
    authentication.getAccessToken();

  if (
    !accessToken
    || request.url.endsWith(
      '/api/v1/auth/login',
    )
  ) {
    return next(request);
  }

  return next(
    request.clone({
      setHeaders: {
        Authorization:
          `Bearer ${accessToken}`,
      },
    }),
  ).pipe(
    catchError(
      (error: HttpErrorResponse) => {
        if (error.status === 401) {
          authentication.logout();

          void router.navigateByUrl(
            '/login',
          );
        }

        return throwError(
          () => error,
        );
      },
    ),
  );
};