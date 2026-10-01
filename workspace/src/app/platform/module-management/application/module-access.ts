import type {
  AuthenticatedUser,
  UserModuleRole,
} from '../../authentication/domain/authenticated-user';

import type { ModuleKey } from '../domain/module-key';

export function getModuleRole(
  user: AuthenticatedUser | null,
  moduleKey: ModuleKey,
): UserModuleRole | null {
  if (!user || user.role === 'platform_admin') {
    return null;
  }

  const access = user.moduleAccess.find(
    item => item.moduleKey === moduleKey,
  );

  return access?.role ?? null;
}

export function canAccessModule(
  user: AuthenticatedUser | null,
  moduleKey: ModuleKey,
): boolean {
  if (!user) {
    return false;
  }

  if (user.role === 'platform_admin') {
    return true;
  }

  return (
    user.enabledModules.includes(moduleKey)
    && user.moduleAccess.some(
      access => access.moduleKey === moduleKey,
    )
  );
}