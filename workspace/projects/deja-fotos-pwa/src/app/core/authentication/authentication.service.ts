import { computed, Injectable, signal } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { Observable, catchError, map, of, switchMap, tap, throwError } from 'rxjs';

export type FotosModuleRole = 'manager' | 'viewer';

export interface FotosAuthenticatedUser {
  id: string;
  organizationId: string | null;
  tenantId: string | null;
  environmentId: string | null;
  name: string;
  email: string;
  role: string;
  fotosRole: FotosModuleRole | null;
}

interface AccessTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

interface ModuleAccessResponse {
  module_key: string;
  role: string;
}

interface AuthenticatedUserResponse {
  id: string;
  organization_id: string | null;
  tenant_id: string | null;
  environment_id: string | null;
  name: string;
  email: string;
  role: string;
  module_access: ModuleAccessResponse[];
}

@Injectable({
  providedIn: 'root',
})
export class AuthenticationService {
  private readonly tokenStorageKey = 'deja-fotos.access-token';

  private readonly userState = signal<FotosAuthenticatedUser | null>(null);

  readonly user = this.userState.asReadonly();

  readonly isAuthenticated = computed(() => this.userState() !== null);

  readonly canAccessFotos = computed(() => {
    const user = this.userState();

    return (
      user?.role === 'platform_admin' ||
      user?.fotosRole === 'manager' ||
      user?.fotosRole === 'viewer'
    );
  });

  constructor(private readonly http: HttpClient) {}

  login(
    organizationCode: string,
    email: string,
    password: string,
  ): Observable<FotosAuthenticatedUser> {
    return this.http
      .post<AccessTokenResponse>('/api/v1/auth/login', {
        organization_code: organizationCode.trim(),
        email: email.trim(),
        password,
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

  restoreSession(): Observable<FotosAuthenticatedUser | null> {
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

  loadCurrentUser(): Observable<FotosAuthenticatedUser> {
    return this.http.get<AuthenticatedUserResponse>('/api/v1/auth/me').pipe(
      map((response) => {
        const fotosAccess = response.module_access.find((access) => access.module_key === 'fotos');

        const fotosRole: FotosModuleRole | null =
          fotosAccess?.role === 'manager' || fotosAccess?.role === 'viewer'
            ? fotosAccess.role
            : null;

        return {
          id: response.id,
          organizationId: response.organization_id,
          tenantId: response.tenant_id,
          environmentId: response.environment_id,
          name: response.name,
          email: response.email,
          role: response.role,
          fotosRole,
        };
      }),
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
