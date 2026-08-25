/*
 * Deja Indicadores
 *
 * Users Domain
 *
 * Erro lançado quando um usuário não é encontrado.
 */

export class UserNotFoundError extends Error {

  constructor(
    id: string,
  ) {
    super(`Usuário não encontrado: ${id}.`);
    this.name = 'UserNotFoundError';
  }

}