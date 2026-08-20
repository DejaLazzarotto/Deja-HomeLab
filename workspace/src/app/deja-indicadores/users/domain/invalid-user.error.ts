/*
 * Deja Indicadores
 *
 * Users Domain
 *
 * Erro de validação dos dados de um usuário.
 */

export class InvalidUserError extends Error {

  constructor(
    message: string,
  ) {
    super(message);
    this.name = 'InvalidUserError';
  }

}