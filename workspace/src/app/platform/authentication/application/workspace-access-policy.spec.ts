import type { AuthenticatedUser } from '../domain/authenticated-user';
import { canAccessWorkspace } from './workspace-access-policy';

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

describe('canAccessWorkspace', () => {
  it('allows platform administrator', () => {
    expect(canAccessWorkspace(
      createUser({ role: 'platform_admin' }),
    )).toBe(true);
  });

  it.each([
    'organization_admin',
    'tenant_admin',
    'manager',
  ] as const)('allows institutional role %s', role => {
    expect(canAccessWorkspace(createUser({ role }))).toBe(true);
  });

  it('allows Vivaro manager', () => {
    expect(canAccessWorkspace(createUser({
      enabledModules: ['fotos'],
      moduleAccess: [{ moduleKey: 'fotos', role: 'manager' }],
    }))).toBe(true);
  });

  it('denies Vivaro viewer', () => {
    expect(canAccessWorkspace(createUser({
      enabledModules: ['fotos'],
      moduleAccess: [{ moduleKey: 'fotos', role: 'viewer' }],
    }))).toBe(false);
  });

  it('denies analyst without management permissions', () => {
    expect(canAccessWorkspace(createUser({
      role: 'analyst',
      enabledModules: ['fotos'],
      moduleAccess: [{ moduleKey: 'fotos', role: 'analyst' }],
    }))).toBe(false);
  });

  it('denies manager of disabled module', () => {
    expect(canAccessWorkspace(createUser({
      moduleAccess: [{ moduleKey: 'fotos', role: 'manager' }],
    }))).toBe(false);
  });

  it('denies ordinary user without modules', () => {
    expect(canAccessWorkspace(createUser())).toBe(false);
  });

  it('denies client', () => {
    expect(canAccessWorkspace(createUser({
      role: 'client',
      enabledModules: ['fotos'],
      moduleAccess: [{ moduleKey: 'fotos', role: 'manager' }],
    }))).toBe(false);
  });

  it('denies unauthenticated user', () => {
    expect(canAccessWorkspace(null)).toBe(false);
  });
});
