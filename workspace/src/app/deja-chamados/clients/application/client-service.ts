/*
 * Deja Chamados
 *
 * Clients Application
 *
 * Serviço de aplicação responsável por coordenar as operações
 * de consulta, criação, atualização e remoção de clientes.
 */

import {
  Client,
  ClientFilters,
  ClientInput,
  ClientNotFoundError,
  ClientRepository,
} from '../domain';

export class ClientService {

  constructor(
    private readonly repository: ClientRepository,
  ) {}

  list(
    filters?: ClientFilters,
  ): Promise<readonly Client[]> {
    return this.repository.list(filters);
  }

  async findById(
    id: string,
  ): Promise<Client> {
    const client = await this.repository.findById(id);

    if (!client) {
      throw new ClientNotFoundError(id);
    }

    return client;
  }

  create(
    input: ClientInput,
  ): Promise<Client> {
    return this.repository.create(input);
  }

  update(
    id: string,
    input: ClientInput,
  ): Promise<Client> {
    return this.repository.update(id, input);
  }

  delete(
    id: string,
  ): Promise<void> {
    return this.repository.delete(id);
  }

}