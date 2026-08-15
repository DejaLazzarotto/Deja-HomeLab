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

  async list(): Promise<readonly Company[]> {
    return Array.from(this.companies.values());
  }

  async findById(
    id: string,
  ): Promise<Company | undefined> {
    return this.companies.get(id);
  }

  async create(
    input: CompanyInput,
  ): Promise<Company> {
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

  async update(
    id: string,
    input: CompanyInput,
  ): Promise<Company> {
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

  async delete(
    id: string,
  ): Promise<void> {
    if (!this.companies.has(id)) {
      throw new CompanyNotFoundError(id);
    }

    this.companies.delete(id);
  }

  private ensureDocumentIsAvailable(
    document: string,
    currentCompanyId?: string,
  ): void {
    const companyWithDocument =
      Array.from(this.companies.values()).find(
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