import { signal } from '@angular/core';

import { TestBed } from '@angular/core/testing';

import {
  ActivatedRouteSnapshot,
  Router,
  RouterStateSnapshot,
} from '@angular/router';

import { of } from 'rxjs';

import {
  AuthenticationService,
} from '../../authentication/application/authentication.service';

import {
  AuthenticatedUser,
} from '../../authentication/domain/authenticated-user';

import {
  moduleGuard,
} from './module.guard';

function createUser(
  overrides: Partial<AuthenticatedUser> = {},
): AuthenticatedUser {
  return {
    id: '11111111-1111-1111-1111-111111111111',
    organizationId: '22222222-2222-2222-2222-222222222222',
    tenantId: null,
    environmentId: null,
    name: 'Usuário Teste',
    email: 'usuario@deja.com',
    role: 'organization_admin',
    enabledModules: [],
    ...overrides,
  };
}

function executeGuard(
  user: AuthenticatedUser | null,
  accessToken: string | null,
): {
  result: ReturnType<ReturnType<typeof moduleGuard>>;
  createUrlTree: ReturnType<typeof vi.fn>;
} {
  const userState = signal(user);
  const createUrlTree = vi.fn((commands: string[]) => ({
    commands,
  }));

  TestBed.configureTestingModule({
    providers: [
      {
        provide: AuthenticationService,
        useValue: {
          user: userState.asReadonly(),
          getAccessToken: () => accessToken,
          restoreSession: () => of(user),
        },
      },
      {
        provide: Router,
        useValue: {
          createUrlTree,
        },
      },
    ],
  });

  const result = TestBed.runInInjectionContext(() =>
    moduleGuard('reports')(
      {} as ActivatedRouteSnapshot,
      {} as RouterStateSnapshot,
    ),
  );

  return {
    result,
    createUrlTree,
  };
}

describe('moduleGuard', () => {
  afterEach(() => {
    TestBed.resetTestingModule();
  });

  it('should allow an enabled module', () => {
    const user = createUser({
      enabledModules: ['reports'],
    });

    const { result, createUrlTree } = executeGuard(
      user,
      'access-token',
    );

    expect(result).toBe(true);
    expect(createUrlTree).not.toHaveBeenCalled();
  });

  it('should redirect a disabled module to the workspace', () => {
    const user = createUser({
      enabledModules: ['indicators'],
    });

    const { result, createUrlTree } = executeGuard(
      user,
      'access-token',
    );

    expect(result).toEqual({
      commands: ['/'],
    });
    expect(createUrlTree).toHaveBeenCalledWith(['/']);
  });

  it('should redirect a missing session to login', () => {
    const { result, createUrlTree } = executeGuard(
      null,
      null,
    );

    expect(result).toEqual({
      commands: ['/login'],
    });
    expect(createUrlTree).toHaveBeenCalledWith(['/login']);
  });
});