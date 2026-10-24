import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import {
  ActivatedRouteSnapshot,
  Router,
  RouterStateSnapshot,
} from '@angular/router';
import { firstValueFrom, isObservable, of } from 'rxjs';

import type { AuthenticatedUser } from '../domain/authenticated-user';
import { AuthenticationService } from './authentication.service';
import { workspaceAccessGuard } from './workspace-access.guard';

function createUser(
  overrides: Partial<AuthenticatedUser> = {},
): AuthenticatedUser {
  return {
    id: 'user-1',
    organizationId: 'org-1',
    tenantId: 'tenant-1',
    environmentId: 'env-1',
    name: 'Usuário Teste',
    email: 'usuario@example.com',
    role: 'user',
    enabledModules: [],
    moduleAccess: [],
    ...overrides,
  };
}

async function executeGuard(
  currentUser: AuthenticatedUser | null,
  restoredUser: AuthenticatedUser | null = currentUser,
  accessToken: string | null = 'access-token',
) {
  const parseUrl = vi.fn((url: string) => ({ url }));
  const restoreSession = vi.fn(() => of(restoredUser));

  TestBed.configureTestingModule({
    providers: [
      {
        provide: AuthenticationService,
        useValue: {
          user: signal(currentUser).asReadonly(),
          getAccessToken: () => accessToken,
          restoreSession,
        },
      },
      {
        provide: Router,
        useValue: { parseUrl },
      },
    ],
  });

  const result = TestBed.runInInjectionContext(() =>
    workspaceAccessGuard(
      {} as ActivatedRouteSnapshot,
      {} as RouterStateSnapshot,
    ),
  );

  const resolved = isObservable(result)
    ? await firstValueFrom(result)
    : await Promise.resolve(result);

  return { resolved, parseUrl, restoreSession };
}

describe('workspaceAccessGuard', () => {
  afterEach(() => TestBed.resetTestingModule());

  it('allows platform administrator', async () => {
    const result = await executeGuard(
      createUser({ role: 'platform_admin' }),
    );
    expect(result.resolved).toBe(true);
  });

  it('allows Vivaro manager', async () => {
    const result = await executeGuard(createUser({
      enabledModules: ['fotos'],
      moduleAccess: [{ moduleKey: 'fotos', role: 'manager' }],
    }));
    expect(result.resolved).toBe(true);
  });

  it('blocks Vivaro viewer', async () => {
    const result = await executeGuard(createUser({
      enabledModules: ['fotos'],
      moduleAccess: [{ moduleKey: 'fotos', role: 'viewer' }],
    }));
    expect(result.resolved).toEqual({ url: '/login' });
  });

  it('redirects client to portal', async () => {
    const result = await executeGuard(
      createUser({ role: 'client' }),
    );
    expect(result.resolved).toEqual({ url: '/portal' });
  });

  it('redirects unauthenticated user to login', async () => {
    const result = await executeGuard(null, null, null);
    expect(result.resolved).toEqual({ url: '/login' });
    expect(result.restoreSession).not.toHaveBeenCalled();
  });

  it('allows restored manager session', async () => {
    const manager = createUser({
      enabledModules: ['fotos'],
      moduleAccess: [{ moduleKey: 'fotos', role: 'manager' }],
    });
    const result = await executeGuard(null, manager);
    expect(result.resolved).toBe(true);
    expect(result.restoreSession).toHaveBeenCalledOnce();
  });

  it('blocks restored viewer session', async () => {
    const viewer = createUser({
      enabledModules: ['fotos'],
      moduleAccess: [{ moduleKey: 'fotos', role: 'viewer' }],
    });
    const result = await executeGuard(null, viewer);
    expect(result.resolved).toEqual({ url: '/login' });
  });

  it('redirects failed session restoration to login', async () => {
    const result = await executeGuard(null, null);
    expect(result.resolved).toEqual({ url: '/login' });
  });
});
