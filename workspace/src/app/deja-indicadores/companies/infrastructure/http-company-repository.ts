/*
 * Deja Indicadores
 *
 * Companies Infrastructure
 *
 * Repositório HTTP responsável pela integração com a FastAPI.
 */

import {
  HttpClient,
  HttpErrorResponse,
} from '@angular/common/http';

import {
  firstValueFrom,
} from 'rxjs';

import {
  Company,
  CompanyInput,
  CompanyRepository,
  CompanyValidator,
} from '../domain';

interface CompanyResponse {
  id: string;
  environment_id: string;
  legal_name: string;
  trade_name: string;
  document: string;
  email: string | null;
  phone: string | null;
  status: Company['status'];
  created_at: string;
  updated_at: string;
}

interface CompanyRequest {
  environment_id: string;
  legal_name: string;
  trade_name: string;
  document: string;
  email: string | null;
  phone: string | null;
  status: Company['status'];
}

export class HttpCompanyRepository implements CompanyRepository {

  private readonly validator = new CompanyValidator();

  constructor(
    private readonly http: HttpClient,
  ) {}

  async list(): Promise<readonly Company[]> {
    const response = await firstValueFrom(
      this.http.get<readonly CompanyResponse[]>(
        '/api/companies',
      ),
    );

    return response.map(company => this.mapCompany(company));
  }

  async findById(
    id: string,
  ): Promise<Company | undefined> {
    try {
      const response = await firstValueFrom(
        this.http.get<CompanyResponse>(
          `/api/companies/${id}`,
        ),
      );

      return this.mapCompany(response);
    } catch (error: unknown) {
      if (
        error instanceof HttpErrorResponse
        && error.status === 404
      ) {
        return undefined;
      }

      throw error;
    }
  }

  async create(
    input: CompanyInput,
  ): Promise<Company> {
    const response = await firstValueFrom(
      this.http.post<CompanyResponse>(
        '/api/companies',
        this.mapRequest(input),
      ),
    );

    return this.mapCompany(response);
  }

  async update(
    id: string,
    input: CompanyInput,
  ): Promise<Company> {
    const response = await firstValueFrom(
      this.http.put<CompanyResponse>(
        `/api/companies/${id}`,
        this.mapRequest(input),
      ),
    );

    return this.mapCompany(response);
  }

  async delete(
    id: string,
  ): Promise<void> {
    await firstValueFrom(
      this.http.delete<void>(
        `/api/companies/${id}`,
      ),
    );
  }

  private mapRequest(
    input: CompanyInput,
  ): CompanyRequest {
    const validatedInput = this.validator.validate(input);

    return {
      environment_id: validatedInput.environmentId,
      legal_name: validatedInput.legalName,
      trade_name: validatedInput.tradeName,
      document: validatedInput.document,
      email: validatedInput.email || null,
      phone: validatedInput.phone || null,
      status: validatedInput.status,
    };
  }

  private mapCompany(
    response: CompanyResponse,
  ): Company {
    return {
      id: response.id,
      environmentId: response.environment_id,
      legalName: response.legal_name,
      tradeName: response.trade_name,
      document: response.document,
      email: response.email ?? '',
      phone: response.phone ?? '',
      status: response.status,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
    };
  }

}