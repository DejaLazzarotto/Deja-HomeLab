export type UserRole =
  | 'platform_admin'
  | 'organization_admin'
  | 'tenant_admin'
  | 'manager'
  | 'analyst'
  | 'viewer';

export interface AuthenticatedUser {
  id: string;
  organizationId: string | null;
  tenantId: string | null;
  environmentId: string | null;
  name: string;
  email: string;
  role: UserRole;
}