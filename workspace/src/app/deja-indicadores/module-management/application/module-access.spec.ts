import { AuthenticatedUser } from '../../authentication/domain/authenticated-user';

import { canAccessModule } from './module-access';

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

describe('canAccessModule', () => {
  it('should deny access without an authenticated user', () => {
    expect(canAccessModule(null, 'indicators')).toBe(false);
  });

  it('should allow an enabled organization module', () => {
    const user = createUser({
      enabledModules: ['indicators'],
    });

    expect(canAccessModule(user, 'indicators')).toBe(true);
  });

  it('should deny a disabled organization module', () => {
    const user = createUser({
      enabledModules: ['measurements'],
    });

    expect(canAccessModule(user, 'reports')).toBe(false);
  });

  it('should allow platform admin administrative access', () => {
    const user = createUser({
      organizationId: null,
      role: 'platform_admin',
      enabledModules: [],
    });

    expect(canAccessModule(user, 'reports')).toBe(true);
  });
});