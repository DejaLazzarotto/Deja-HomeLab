/*
 * Deja Indicadores
 *
 * Measurements Infrastructure
 *
 * Repositório HTTP responsável pela integração com a FastAPI.
 */

import {
  HttpClient,
  HttpErrorResponse,
  HttpParams,
} from '@angular/common/http';

import {
  firstValueFrom,
} from 'rxjs';

import {
  Measurement,
  MeasurementFilters,
  MeasurementInput,
  MeasurementRepository,
  MeasurementValidator,
} from '../domain';

interface MeasurementResponse {
  id: string;
  indicator_id: string;
  reference_date: string;
  actual_value: number | string;
  observation: string | null;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

interface MeasurementRequest {
  indicator_id: string;
  reference_date: string;
  actual_value: number;
  observation: string | null;
}

export class HttpMeasurementRepository
implements MeasurementRepository {

  private readonly validator =
    new MeasurementValidator();

  constructor(
    private readonly http: HttpClient,
  ) {}

  async list(
    filters: MeasurementFilters = {},
  ): Promise<readonly Measurement[]> {
    let params = new HttpParams();

    if (filters.companyId) {
      params = params.set(
        'company_id',
        filters.companyId,
      );
    }

    if (filters.indicatorId) {
      params = params.set(
        'indicator_id',
        filters.indicatorId,
      );
    }

    if (filters.startDate) {
      params = params.set(
        'start_date',
        filters.startDate,
      );
    }

    if (filters.endDate) {
      params = params.set(
        'end_date',
        filters.endDate,
      );
    }

    const response = await firstValueFrom(
      this.http.get<readonly MeasurementResponse[]>(
        '/api/measurements',
        {
          params,
        },
      ),
    );

    return response.map(
      measurement =>
        this.mapMeasurement(measurement),
    );
  }

  async findById(
    id: string,
  ): Promise<Measurement | undefined> {
    try {
      const response = await firstValueFrom(
        this.http.get<MeasurementResponse>(
          `/api/measurements/${id}`,
        ),
      );

      return this.mapMeasurement(response);
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
    input: MeasurementInput,
  ): Promise<Measurement> {
    const response = await firstValueFrom(
      this.http.post<MeasurementResponse>(
        '/api/measurements',
        this.mapRequest(input),
      ),
    );

    return this.mapMeasurement(response);
  }

  async update(
    id: string,
    input: MeasurementInput,
  ): Promise<Measurement> {
    const response = await firstValueFrom(
      this.http.put<MeasurementResponse>(
        `/api/measurements/${id}`,
        this.mapRequest(input),
      ),
    );

    return this.mapMeasurement(response);
  }

  async delete(
    id: string,
  ): Promise<void> {
    await firstValueFrom(
      this.http.delete<void>(
        `/api/measurements/${id}`,
      ),
    );
  }

  private mapRequest(
    input: MeasurementInput,
  ): MeasurementRequest {
    const validatedInput =
      this.validator.validate(input);

    return {
      indicator_id: validatedInput.indicatorId,
      reference_date: validatedInput.referenceDate,
      actual_value: validatedInput.actualValue,
      observation:
        validatedInput.observation || null,
    };
  }

  private mapMeasurement(
    response: MeasurementResponse,
  ): Measurement {
    return {
      id: response.id,
      indicatorId: response.indicator_id,
      referenceDate: response.reference_date,
      actualValue: Number(response.actual_value),
      observation: response.observation ?? '',
      createdBy: response.created_by,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
    };
  }

}