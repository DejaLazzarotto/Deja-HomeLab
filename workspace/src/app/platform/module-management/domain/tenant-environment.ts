export type TenantEnvironmentStatus =
  | 'provisioning'
  | 'active'
  | 'inactive';

export interface Tenant {
  readonly id: string;
  readonly organizationId: string;
  readonly name: string;
  readonly status: TenantEnvironmentStatus;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export interface TenantInput {
  organizationId: string;
  name: string;
  status: TenantEnvironmentStatus;
}

export interface Environment {
  readonly id: string;
  readonly tenantId: string;
  readonly name: string;
  readonly status: TenantEnvironmentStatus;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export interface EnvironmentInput {
  tenantId: string;
  name: string;
  status: TenantEnvironmentStatus;
}