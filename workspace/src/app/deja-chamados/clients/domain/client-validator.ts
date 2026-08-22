/*
 * Deja Chamados
 *
 * Clients Domain
 *
 * Valida e normaliza os dados de entrada de um cliente.
 */

import {
  ClientInput,
} from './client';

import {
  InvalidClientError,
} from './invalid-client.error';

export class ClientValidator {

  validate(
    input: ClientInput,
  ): ClientInput {
    const environmentId = this.requireText(
      input.environmentId,
      'O ambiente é obrigatório.',
    );

    const companyName = this.requireText(
      input.companyName,
      'A razão social é obrigatória.',
      255,
    );

    const fantasyName = this.requireText(
      input.fantasyName,
      'O nome fantasia é obrigatório.',
      255,
    );

    const document = this.onlyDigits(
      this.requireText(
        input.document,
        'O documento é obrigatório.',
      ),
    );

    if (
      document.length !== 11
      && document.length !== 14
    ) {
      throw new InvalidClientError(
        'O documento deve ser um CPF ou CNPJ válido.',
      );
    }

    const contactName = this.requireText(
      input.contactName,
      'O nome do contato é obrigatório.',
      255,
    );

    const phone = this.validatePhone(
      input.phone,
      'O telefone é inválido.',
    );

    const whatsapp = this.validatePhone(
      input.whatsapp,
      'O WhatsApp é inválido.',
    );

    const email = this.requireText(
      input.email,
      'O e-mail é obrigatório.',
      255,
    ).toLowerCase();

    if (
      !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)
    ) {
      throw new InvalidClientError(
        'O e-mail é inválido.',
      );
    }

    const city = this.requireText(
      input.city,
      'A cidade é obrigatória.',
      100,
    );

    const state = this.requireText(
      input.state,
      'O estado é obrigatório.',
      2,
    ).toUpperCase();

    if (state.length !== 2) {
      throw new InvalidClientError(
        'O estado deve possuir duas letras.',
      );
    }

    const notes = String(
      input.notes ?? '',
    ).trim();

    if (notes.length > 1000) {
      throw new InvalidClientError(
        'As observações devem possuir no máximo 1000 caracteres.',
      );
    }

    return {
      environmentId,
      companyName,
      fantasyName,
      document,
      contactName,
      phone,
      whatsapp,
      email,
      city,
      state,
      notes,
      active: Boolean(input.active),
    };
  }

  private requireText(
    value: string,
    message: string,
    maximumLength?: number,
  ): string {
    const normalizedValue = String(
      value ?? '',
    ).trim();

    if (!normalizedValue) {
      throw new InvalidClientError(
        message,
      );
    }

    if (
      maximumLength !== undefined
      && normalizedValue.length > maximumLength
    ) {
      throw new InvalidClientError(
        message,
      );
    }

    return normalizedValue;
  }

  private validatePhone(
    value: string,
    message: string,
  ): string {
    const normalizedValue = this.onlyDigits(
      this.requireText(
        value,
        message,
      ),
    );

    if (
      normalizedValue.length !== 10
      && normalizedValue.length !== 11
    ) {
      throw new InvalidClientError(
        message,
      );
    }

    return normalizedValue;
  }

  private onlyDigits(
    value: string,
  ): string {
    return value.replace(/\D/g, '');
  }

}