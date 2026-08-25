/*
 * Deja Indicadores
 *
 * Users Domain
 *
 * Contrato de persistência da Gestão de Usuários.
 */

import {
  User,
} from './user';

import {
  UserFilters,
} from './user-filters';

import {
  UserInput,
} from './user-input';

export interface UserRepository {

  list(
    filters?: UserFilters,
  ): Promise<readonly User[]>;

  findById(
    id: string,
  ): Promise<User | undefined>;

  create(
    input: UserInput,
  ): Promise<User>;

  update(
    id: string,
    input: UserInput,
  ): Promise<User>;

  setPassword(
    id: string,
    password: string,
  ): Promise<User>;

}