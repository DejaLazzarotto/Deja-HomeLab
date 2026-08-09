/*
 * Deja Indicadores
 *
 * Companies Domain
 *
 * Validação e normalização institucional dos dados de empresas.
 */

import {
  CompanyInput,
} from './company-input';

import {
  InvalidCompanyError,
} from './invalid-company.error';

export class CompanyValidator {

  validate(
    input: CompanyInput,
  ): CompanyInput {
    const normalizedInput: CompanyInput = {
      legalName: input.legalName.trim(),
      tradeName: input.tradeName.trim(),
      document: this.normalizeDocument(input.document),
      email: input.email.trim().toLowerCase(),
      phone: input.phone.trim(),
      status: input.status,
    };

    if (!normalizedInput.legalName) {
      throw new InvalidCompanyError(
        'legalName',
        'Company legal name is required.',
      );
    }

    if (!normalizedInput.tradeName) {
      throw new InvalidCompanyError(
        'tradeName',
        'Company trade name is required.',
      );
    }

    if (!normalizedInput.document) {
      throw new InvalidCompanyError(
        'document',
        'Company document is required.',
      );
    }

    if (
      normalizedInput.email
      && !this.isValidEmail(normalizedInput.email)
    ) {
      throw new InvalidCompanyError(
        'email',
        'Company email is invalid.',
      );
    }

    return normalizedInput;
  }

  private normalizeDocument(
    document: string,
  ): string {
    return document.replace(/\D/g, '');
  }

  private isValidEmail(
    email: string,
  ): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

}