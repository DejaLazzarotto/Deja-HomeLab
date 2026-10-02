/*
 * Deja Indicadores
 *
 * Users Application
 *
 * Serviço de aplicação responsável pela Gestão de Usuários.
 */

import {
  InvalidUserError,
  User,
  UserFilters,
  UserInput,
  UserModuleAccesses,
  UserModuleAccessSelection,
  UserNotFoundError,
  UserRepository,
} from '../domain';

export class UserService {
  constructor(private readonly repository: UserRepository) {}

  list(filters?: UserFilters): Promise<readonly User[]> {
    return this.repository.list(filters);
  }

  async findById(id: string): Promise<User> {
    const user = await this.repository.findById(id);

    if (!user) {
      throw new UserNotFoundError(id);
    }

    return user;
  }

  create(input: UserInput): Promise<User> {
    return this.repository.create(input);
  }

  update(id: string, input: UserInput): Promise<User> {
    return this.repository.update(id, input);
  }

  setPassword(id: string, password: string): Promise<User> {
    if (password.length < 8 || password.length > 128) {
      throw new InvalidUserError('A senha deve possuir entre 8 e 128 caracteres.');
    }

    return this.repository.setPassword(id, password);
  }

  getModuleAccesses(id: string): Promise<UserModuleAccesses> {
    return this.repository.getModuleAccesses(id);
  }

  updateModuleAccesses(
    id: string,
    modules: readonly UserModuleAccessSelection[],
  ): Promise<UserModuleAccesses> {
    return this.repository.updateModuleAccesses(id, modules);
  }
}
