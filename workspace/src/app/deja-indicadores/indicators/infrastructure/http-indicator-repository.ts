/*
 * Deja Indicadores
 *
 * Indicators Infrastructure
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
  Indicator,
  IndicatorInput,
  IndicatorRepository,
  IndicatorValidator,
} from '../domain';

interface IndicatorResponse {
  id: string;
  company_id: string;
  name: string;
  description: string | null;
  unit: string;
  direction: Indicator['direction'];
  target_value: number | string;
  status: Indicator['status'];
  created_at: string;
  updated_at: string;
}

interface IndicatorRequest {
  company_id: string;
  name: string;
  description: string | null;
  unit: string;
  direction: Indicator['direction'];
  target_value: number;
  status: Indicator['status'];
}

export class HttpIndicatorRepository
implements IndicatorRepository {

  private readonly validator =
    new IndicatorValidator();

  constructor(
    private readonly http: HttpClient,
  ) {}

  async list(): Promise<readonly Indicator[]> {
    const response = await firstValueFrom(
      this.http.get<readonly IndicatorResponse[]>(
        '/api/indicators',
      ),
    );

    return response.map(
      indicator => this.mapIndicator(indicator),
    );
  }

  async findById(
    id: string,
  ): Promise<Indicator | undefined> {
    try {
      const response = await firstValueFrom(
        this.http.get<IndicatorResponse>(
          `/api/indicators/${id}`,
        ),
      );

      return this.mapIndicator(response);
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
    input: IndicatorInput,
  ): Promise<Indicator> {
    const response = await firstValueFrom(
      this.http.post<IndicatorResponse>(
        '/api/indicators',
        this.mapRequest(input),
      ),
    );

    return this.mapIndicator(response);
  }

  async update(
    id: string,
    input: IndicatorInput,
  ): Promise<Indicator> {
    const response = await firstValueFrom(
      this.http.put<IndicatorResponse>(
        `/api/indicators/${id}`,
        this.mapRequest(input),
      ),
    );

    return this.mapIndicator(response);
  }

  async delete(
    id: string,
  ): Promise<void> {
    await firstValueFrom(
      this.http.delete<void>(
        `/api/indicators/${id}`,
      ),
    );
  }

  private mapRequest(
    input: IndicatorInput,
  ): IndicatorRequest {
    const validatedInput =
      this.validator.validate(input);

    return {
      company_id: validatedInput.companyId,
      name: validatedInput.name,
      description:
        validatedInput.description || null,
      unit: validatedInput.unit,
      direction: validatedInput.direction,
      target_value: validatedInput.targetValue,
      status: validatedInput.status,
    };
  }

  private mapIndicator(
    response: IndicatorResponse,
  ): Indicator {
    return {
      id: response.id,
      companyId: response.company_id,
      name: response.name,
      description: response.description ?? '',
      unit: response.unit,
      direction: response.direction,
      targetValue: Number(response.target_value),
      status: response.status,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
    };
  }

}