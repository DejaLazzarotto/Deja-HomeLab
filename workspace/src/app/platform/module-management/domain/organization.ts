export type OrganizationStatus =
  | 'provisioning'
  | 'active'
  | 'inactive';

export interface Organization {
  readonly id: string;
  readonly code: string;
  readonly name: string;
  readonly status: OrganizationStatus;
  readonly createdAt: string;
  readonly updatedAt: string;
}