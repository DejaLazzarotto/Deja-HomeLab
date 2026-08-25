import type { AuthenticatedUser } from '../../authentication/domain/authenticated-user';

import type { ModuleKey } from '../domain/module-key';

export function canAccessModule(
  user: AuthenticatedUser | null,
  moduleKey: ModuleKey,
): boolean {
  if (!user) {
    return false;
  }

  return user.role === 'platform_admin' || user.enabledModules.includes(moduleKey);
}