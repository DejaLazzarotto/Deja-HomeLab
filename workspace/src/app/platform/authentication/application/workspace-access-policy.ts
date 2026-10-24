import type {
  AuthenticatedUser,
} from '../domain/authenticated-user';

export function canAccessWorkspace(
  user: AuthenticatedUser | null,
): boolean {
  if (!user || user.role === 'client') {
    return false;
  }

  if (
    user.role === 'platform_admin'
    || user.role === 'organization_admin'
    || user.role === 'tenant_admin'
    || user.role === 'manager'
  ) {
    return true;
  }

  return user.moduleAccess.some(
    access =>
      access.role === 'manager'
      && user.enabledModules.includes(access.moduleKey),
  );
}
