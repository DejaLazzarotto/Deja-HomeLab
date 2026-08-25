import {
  OrganizationStatus,
} from './organization';

export interface OrganizationInput {
  code: string;
  name: string;
  status: OrganizationStatus;
}