import { ModuleKey } from '../../module-management/domain/module-key';

export type UserRole =
  | 'platform_admin'
  | 'organization_admin'
  | 'tenant_admin'
  | 'manager'
  | 'analyst'
  | 'viewer'
  | 'client';

export type UserModuleRole =
  | 'manager'
  | 'analyst'
  | 'viewer';

export interface AuthenticatedModuleAccess {
  moduleKey: ModuleKey;
  role: UserModuleRole;
}

export interface AuthenticatedUser {
  id: string;
  organizationId: string | null;
  tenantId: string | null;
  environmentId: string | null;
  name: string;
  email: string;
  role: UserRole;
  enabledModules: readonly ModuleKey[];
  moduleAccess: readonly AuthenticatedModuleAccess[];
}