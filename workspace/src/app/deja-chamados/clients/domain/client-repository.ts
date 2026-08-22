/*
 * Deja Chamados
 *
 * Clients Domain
 *
 * Contrato de persistência dos clientes do módulo.
 */

import {
  Client,
  ClientInput,
} from './client';

import {
  ClientFilters,
} from './client-filters';

export interface ClientRepository {

  list(
    filters?: ClientFilters,
  ): Promise<readonly Client[]>;

  findById(
    id: string,
  ): Promise<Client | undefined>;

  create(
    input: ClientInput,
  ): Promise<Client>;

  update(
    id: string,
    input: ClientInput,
  ): Promise<Client>;

  delete(
    id: string,
  ): Promise<void>;

}