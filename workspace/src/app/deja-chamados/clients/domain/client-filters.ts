/*
 * Deja Chamados
 *
 * Clients Domain
 *
 * Filtros disponíveis para consulta de clientes.
 */

export interface ClientFilters {
  organizationId?: string;
  tenantId?: string;
  environmentId?: string;

  search?: string;
  active?: boolean;
}