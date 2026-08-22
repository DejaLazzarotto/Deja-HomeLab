import { computed, Injectable, signal } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { Observable, catchError, map, of, switchMap, tap, throwError } from 'rxjs';

import { AuthenticatedUser } from '../domain/authenticated-user';

import { LoginCredentials } from '../domain/login-credentials';

interface AccessTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

interface AuthenticatedUserResponse {
  id: string;
  organization_id: string | null;
  tenant_id: string | null;
  environment_id: string | null;
  name: string;
  email: string;
  role: AuthenticatedUser['role'];
}

@Injectable({
  providedIn: 'root',
})
export class AuthenticationService {
  private readonly tokenStorageKey = 'deja-indicadores.access-token';

  private readonly userState = signal<AuthenticatedUser | null>(null);

  readonly user = this.userState.asReadonly();

  readonly isAuthenticated = computed(() => this.userState() !== null);

  constructor(private readonly http: HttpClient) {}

  login(credentials: LoginCredentials): Observable<AuthenticatedUser> {
    return this.http
      .post<AccessTokenResponse>('/api/v1/auth/login', {
        organization_code: credentials.organizationCode,
        email: credentials.email,
        password: credentials.password,
      })
      .pipe(
        tap((response) => {
          localStorage.setItem(this.tokenStorageKey, response.access_token);
        }),
        switchMap(() => this.loadCurrentUser()),
        catchError((error) => {
          this.clearSession();
          return throwError(() => error);
        }),
      );
  }

  restoreSession(): Observable<AuthenticatedUser | null> {
    if (!this.getAccessToken()) {
      return of(null);
    }

    return this.loadCurrentUser().pipe(
      catchError(() => {
        this.clearSession();
        return of(null);
      }),
    );
  }

  loadCurrentUser(): Observable<AuthenticatedUser> {
    return this.http.get<AuthenticatedUserResponse>('/api/v1/auth/me').pipe(
      map((response) => ({
        id: response.id,
        organizationId: response.organization_id,
        tenantId: response.tenant_id,
        environmentId: response.environment_id,
        name: response.name,
        email: response.email,
        role: response.role,
      })),
      tap((user) => {
        this.userState.set(user);
      }),
    );
  }

  logout(): void {
    this.clearSession();
  }

  getAccessToken(): string | null {
    return localStorage.getItem(this.tokenStorageKey);
  }

  private clearSession(): void {
    localStorage.removeItem(this.tokenStorageKey);

    this.userState.set(null);
  }
}
