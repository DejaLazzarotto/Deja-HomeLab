import { AuthenticatedUser } from '../../authentication/domain/authenticated-user';

import {
  canAccessModule,
  getModuleRole,
} from './module-access';

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
    moduleAccess: [],
    ...overrides,
  };
}

describe('canAccessModule', () => {
  it('should deny access without an authenticated user', () => {
    expect(canAccessModule(null, 'indicators')).toBe(false);
  });

  it('should allow an enabled module assigned to the user', () => {
    const user = createUser({
      enabledModules: ['indicators'],
      moduleAccess: [
        {
          moduleKey: 'indicators',
          role: 'analyst',
        },
      ],
    });

    expect(canAccessModule(user, 'indicators')).toBe(true);
  });

  it('should deny an enabled module without user access', () => {
    const user = createUser({
      enabledModules: ['reports'],
      moduleAccess: [],
    });

    expect(canAccessModule(user, 'reports')).toBe(false);
  });

  it('should deny user access when organization module is disabled', () => {
    const user = createUser({
      enabledModules: ['indicators'],
      moduleAccess: [
        {
          moduleKey: 'reports',
          role: 'viewer',
        },
      ],
    });

    expect(canAccessModule(user, 'reports')).toBe(false);
  });

  it('should allow platform admin administrative access', () => {
    const user = createUser({
      organizationId: null,
      role: 'platform_admin',
      enabledModules: [],
      moduleAccess: [],
    });

    expect(canAccessModule(user, 'reports')).toBe(true);
  });
});

describe('getModuleRole', () => {
  it('should return the assigned functional role', () => {
    const user = createUser({
      enabledModules: ['fotos'],
      moduleAccess: [
        {
          moduleKey: 'fotos',
          role: 'manager',
        },
      ],
    });

    expect(getModuleRole(user, 'fotos')).toBe('manager');
  });

  it('should return null without module access', () => {
    const user = createUser({
      enabledModules: ['fotos'],
      moduleAccess: [],
    });

    expect(getModuleRole(user, 'fotos')).toBeNull();
  });

  it('should return null for platform admin', () => {
    const user = createUser({
      organizationId: null,
      role: 'platform_admin',
      moduleAccess: [],
    });

    expect(getModuleRole(user, 'fotos')).toBeNull();
  });
});