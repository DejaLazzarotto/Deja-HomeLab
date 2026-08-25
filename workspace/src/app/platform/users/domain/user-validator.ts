/*
 * Deja Indicadores
 *
 * Users Domain
 *
 * Validação dos dados e do escopo institucional de usuários.
 */

import {
  InvalidUserError,
} from './invalid-user.error';

import {
  UserInput,
} from './user-input';

export class UserValidator {

  validate(
    input: UserInput,
  ): UserInput {
    const name = input.name.trim();
    const email = input.email.trim().toLowerCase();

    if (!name) {
      throw new InvalidUserError(
        'Informe o nome do usuário.',
      );
    }

    if (
      !email
      || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
    ) {
      throw new InvalidUserError(
        'Informe um e-mail válido.',
      );
    }

    this.validateScope(input);

    return {
      ...input,
      name,
      email,
    };
  }

  private validateScope(
    input: UserInput,
  ): void {
    if (input.role === 'platform_admin') {
      if (
        input.organizationId
        || input.tenantId
        || input.environmentId
      ) {
        throw new InvalidUserError(
          'Administrador da plataforma não permite organização, tenant ou ambiente.',
        );
      }

      return;
    }

    if (!input.organizationId) {
      throw new InvalidUserError(
        'Selecione a organização do usuário.',
      );
    }

    if (input.role === 'organization_admin') {
      if (input.tenantId || input.environmentId) {
        throw new InvalidUserError(
          'Administrador da organização não permite tenant ou ambiente.',
        );
      }

      return;
    }

    if (input.role === 'tenant_admin') {
      if (!input.tenantId || input.environmentId) {
        throw new InvalidUserError(
          'Administrador do tenant exige tenant e não permite ambiente.',
        );
      }

      return;
    }

    if (!input.tenantId || !input.environmentId) {
      throw new InvalidUserError(
        'O papel selecionado exige tenant e ambiente.',
      );
    }
  }

}