/*
 * Deja Indicadores
 *
 * Users Domain
 *
 * Representação de um usuário institucional administrado.
 */

import {
  UserRole,
} from '../../authentication/domain/authenticated-user';

export type UserStatus =
  | 'active'
  | 'inactive';

export interface User {
  readonly id: string;
  readonly organizationId: string | null;
  readonly tenantId: string | null;
  readonly environmentId: string | null;
  readonly name: string;
  readonly email: string;
  readonly role: UserRole;
  readonly status: UserStatus;
  readonly createdAt: string;
  readonly updatedAt: string;
}