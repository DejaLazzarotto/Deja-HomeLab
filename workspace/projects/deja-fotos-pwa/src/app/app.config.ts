import { isDevMode } from '@angular/core';
import { provideServiceWorker } from '@angular/service-worker';
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
} from './core/authentication/authentication.interceptor';

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
    provideServiceWorker('ngsw-worker.js', {
      enabled: !isDevMode(),
      registrationStrategy: 'registerWhenStable:30000',
    }),
  ],
};