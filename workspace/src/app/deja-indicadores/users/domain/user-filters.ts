/*
 * Deja Indicadores
 *
 * Users Domain
 *
 * Filtros disponíveis para consulta de usuários.
 */

import {
  UserStatus,
} from './user';

export interface UserFilters {
  readonly organizationId?: string | null;
  readonly tenantId?: string | null;
  readonly environmentId?: string | null;
  readonly status?: UserStatus | null;
}