import {
  ApplicationConfig,
  provideBrowserGlobalErrorListeners,
} from '@angular/core';

import {
  provideHttpClient,
  withInterceptors,
} from '@angular/common/http';

import {
  provideRouter,
} from '@angular/router';

import {
  authenticationInterceptor,
} from './platform/authentication/infrastructure/authentication.interceptor';

import {
  routes,
} from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideHttpClient(
      withInterceptors([
        authenticationInterceptor,
      ]),
    ),
    provideRouter(routes),
  ],
};
