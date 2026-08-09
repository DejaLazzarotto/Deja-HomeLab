/*
 * Deja Indicadores
 *
 * Companies Infrastructure
 *
 * Repositório local em memória para persistência e consulta de empresas.
 */

import {
  Company,
} from '../domain/company';

import {
  CompanyDocumentAlreadyExistsError,
} from '../domain/company-document-already-exists.error';

import {
  CompanyInput,
} from '../domain/company-input';

import {
  CompanyNotFoundError,
} from '../domain/company-not-found.error';

import {
  CompanyRepository,
} from '../domain/company-repository';

import {
  CompanyValidator,
} from '../domain/company-validator';

export class InMemoryCompanyRepository implements CompanyRepository {

  private readonly companies = new Map<string, Company>();

  private readonly validator = new CompanyValidator();

  list(): readonly Company[] {
    return Array.from(this.companies.values());
  }

  findById(
    id: string,
  ): Company | undefined {
    return this.companies.get(id);
  }

  create(
    input: CompanyInput,
  ): Company {
    const validatedInput = this.validator.validate(input);

    this.ensureDocumentIsAvailable(validatedInput.document);

    const timestamp = new Date().toISOString();

    const company: Company = {
      id: crypto.randomUUID(),
      ...validatedInput,
      createdAt: timestamp,
      updatedAt: timestamp,
    };

    this.companies.set(company.id, company);

    return company;
  }

  update(
    id: string,
    input: CompanyInput,
  ): Company {
    const currentCompany = this.companies.get(id);

    if (!currentCompany) {
      throw new CompanyNotFoundError(id);
    }

    const validatedInput = this.validator.validate(input);

    this.ensureDocumentIsAvailable(
      validatedInput.document,
      id,
    );

    const company: Company = {
      ...currentCompany,
      ...validatedInput,
      updatedAt: new Date().toISOString(),
    };

    this.companies.set(company.id, company);

    return company;
  }

  delete(
    id: string,
  ): void {
    if (!this.companies.has(id)) {
      throw new CompanyNotFoundError(id);
    }

    this.companies.delete(id);
  }

  private ensureDocumentIsAvailable(
    document: string,
    currentCompanyId?: string,
  ): void {
    const companyWithDocument = this.list().find(
      company => (
        company.document === document
        && company.id !== currentCompanyId
      ),
    );

    if (companyWithDocument) {
      throw new CompanyDocumentAlreadyExistsError(document);
    }
  }

}