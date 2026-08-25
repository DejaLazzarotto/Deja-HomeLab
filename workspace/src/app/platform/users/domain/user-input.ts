/*
 * Deja Indicadores
 *
 * Users Domain
 *
 * Dados aceitos no cadastro e na edição de usuários.
 */

import {
  UserRole,
} from '../../authentication/domain/authenticated-user';

import {
  UserStatus,
} from './user';

export interface UserInput {
  organizationId: string | null;
  tenantId: string | null;
  environmentId: string | null;
  name: string;
  email: string;
  role: UserRole;
  status: UserStatus;
}