import {
  HttpClient,
  provideHttpClient,
} from '@angular/common/http';

import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';

import {
  TestBed,
} from '@angular/core/testing';

import {
  IndicatorInput,
} from '../domain';

import {
  HttpIndicatorRepository,
} from './http-indicator-repository';

describe('HttpIndicatorRepository', () => {

  let repository: HttpIndicatorRepository;
  let httpTesting: HttpTestingController;

  const companyId =
    '11111111-1111-1111-1111-111111111111';

  const indicatorResponse = {
    id: '22222222-2222-2222-2222-222222222222',
    company_id: companyId,
    name: 'Faturamento mensal',
    description: 'Faturamento consolidado.',
    unit: 'R$',
    direction: 'higher_is_better' as const,
    target_value: '150000.5000',
    status: 'active' as const,
    created_at: '2026-08-20T10:00:00',
    updated_at: '2026-08-20T10:00:00',
  };

  const input: IndicatorInput = {
    companyId,
    name: ' Faturamento mensal ',
    description: ' Faturamento consolidado. ',
    unit: ' R$ ',
    direction: 'higher_is_better',
    targetValue: 150000.5,
    status: 'active',
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    repository = new HttpIndicatorRepository(
      TestBed.inject(HttpClient),
    );

    httpTesting =
      TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('should list and map indicators from the API', async () => {
    const resultPromise = repository.list();

    const request =
      httpTesting.expectOne('/api/indicators');

    expect(request.request.method).toBe('GET');

    request.flush([
      indicatorResponse,
    ]);

    await expect(resultPromise).resolves.toEqual([
      {
        id: indicatorResponse.id,
        companyId,
        name: indicatorResponse.name,
        description: indicatorResponse.description,
        unit: indicatorResponse.unit,
        direction: indicatorResponse.direction,
        targetValue: 150000.5,
        status: indicatorResponse.status,
        createdAt: indicatorResponse.created_at,
        updatedAt: indicatorResponse.updated_at,
      },
    ]);
  });

  it('should normalize and create an indicator', async () => {
    const resultPromise = repository.create(input);

    const request =
      httpTesting.expectOne('/api/indicators');

    expect(request.request.method).toBe('POST');

    expect(request.request.body).toEqual({
      company_id: companyId,
      name: 'Faturamento mensal',
      description: 'Faturamento consolidado.',
      unit: 'R$',
      direction: 'higher_is_better',
      target_value: 150000.5,
      status: 'active',
    });

    request.flush(indicatorResponse);

    await expect(resultPromise).resolves.toMatchObject({
      companyId,
      name: 'Faturamento mensal',
      unit: 'R$',
      targetValue: 150000.5,
    });
  });

  it('should update and delete an indicator', async () => {
    const updatePromise = repository.update(
      indicatorResponse.id,
      input,
    );

    const updateRequest =
      httpTesting.expectOne(
        `/api/indicators/${indicatorResponse.id}`,
      );

    expect(updateRequest.request.method).toBe('PUT');

    updateRequest.flush(indicatorResponse);

    await updatePromise;

    const deletePromise = repository.delete(
      indicatorResponse.id,
    );

    const deleteRequest =
      httpTesting.expectOne(
        `/api/indicators/${indicatorResponse.id}`,
      );

    expect(deleteRequest.request.method).toBe('DELETE');

    deleteRequest.flush(null);

    await expect(deletePromise).resolves.toBeUndefined();
  });

});