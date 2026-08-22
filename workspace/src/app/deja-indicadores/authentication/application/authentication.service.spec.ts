import { provideHttpClient } from '@angular/common/http';

import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

import { TestBed } from '@angular/core/testing';

import { firstValueFrom } from 'rxjs';

import { AuthenticationService } from './authentication.service';

describe('AuthenticationService', () => {
  let service: AuthenticationService;
  let httpTesting: HttpTestingController;

  const organizationId = '11111111-1111-1111-1111-111111111111';

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });

    service = TestBed.inject(AuthenticationService);
    httpTesting = TestBed.inject(HttpTestingController);

    localStorage.clear();
  });

  afterEach(() => {
    httpTesting.verify();
    localStorage.clear();
  });

  it('should authenticate with the organization code', async () => {
    const resultPromise = firstValueFrom(
      service.login({
        organizationCode: 'ORG-PRINCIPAL',
        email: 'usuario@deja.com',
        password: 'SenhaSegura123!',
      }),
    );

    const loginRequest = httpTesting.expectOne('/api/v1/auth/login');

    expect(loginRequest.request.method).toBe('POST');

    expect(loginRequest.request.body).toEqual({
      organization_code: 'ORG-PRINCIPAL',
      email: 'usuario@deja.com',
      password: 'SenhaSegura123!',
    });

    loginRequest.flush({
      access_token: 'access-token',
      token_type: 'bearer',
      expires_in: 1800,
    });

    const currentUserRequest = httpTesting.expectOne('/api/v1/auth/me');

    expect(currentUserRequest.request.method).toBe('GET');

    currentUserRequest.flush({
      id: '22222222-2222-2222-2222-222222222222',
      organization_id: organizationId,
      tenant_id: null,
      environment_id: null,
      name: 'Usuário Teste',
      email: 'usuario@deja.com',
      role: 'organization_admin',
    });

    await expect(resultPromise).resolves.toEqual({
      id: '22222222-2222-2222-2222-222222222222',
      organizationId,
      tenantId: null,
      environmentId: null,
      name: 'Usuário Teste',
      email: 'usuario@deja.com',
      role: 'organization_admin',
    });

    expect(localStorage.getItem('deja-indicadores.access-token')).toBe('access-token');
  });

  it('should authenticate a platform admin without organization', async () => {
    const resultPromise = firstValueFrom(
      service.login({
        organizationCode: null,
        email: 'platform.admin@deja.com',
        password: 'SenhaSegura123!',
      }),
    );

    const loginRequest = httpTesting.expectOne('/api/v1/auth/login');

    expect(loginRequest.request.method).toBe('POST');

    expect(loginRequest.request.body).toEqual({
      organization_code: null,
      email: 'platform.admin@deja.com',
      password: 'SenhaSegura123!',
    });

    loginRequest.flush({
      access_token: 'platform-access-token',
      token_type: 'bearer',
      expires_in: 1800,
    });

    const currentUserRequest = httpTesting.expectOne('/api/v1/auth/me');

    currentUserRequest.flush({
      id: '33333333-3333-3333-3333-333333333333',
      organization_id: null,
      tenant_id: null,
      environment_id: null,
      name: 'Platform Admin',
      email: 'platform.admin@deja.com',
      role: 'platform_admin',
    });

    await expect(resultPromise).resolves.toMatchObject({
      organizationId: null,
      tenantId: null,
      environmentId: null,
      role: 'platform_admin',
    });
  });
});
