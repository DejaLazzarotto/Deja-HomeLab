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
  MeasurementInput,
} from '../domain';

import {
  HttpMeasurementRepository,
} from './http-measurement-repository';

describe('HttpMeasurementRepository', () => {

  let repository: HttpMeasurementRepository;
  let httpTesting: HttpTestingController;

  const companyId =
    '11111111-1111-1111-1111-111111111111';

  const indicatorId =
    '22222222-2222-2222-2222-222222222222';

  const measurementResponse = {
    id: '33333333-3333-3333-3333-333333333333',
    indicator_id: indicatorId,
    reference_date: '2026-08-20',
    actual_value: '125.5000',
    observation: 'Valor conferido.',
    created_by:
      '44444444-4444-4444-4444-444444444444',
    created_at: '2026-08-20T10:00:00',
    updated_at: '2026-08-20T10:00:00',
  };

  const input: MeasurementInput = {
    indicatorId: ` ${indicatorId} `,
    referenceDate: '2026-08-20',
    actualValue: 125.5,
    observation: ' Valor conferido. ',
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    repository = new HttpMeasurementRepository(
      TestBed.inject(HttpClient),
    );

    httpTesting =
      TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('should list and map filtered measurements', async () => {
    const resultPromise = repository.list({
      companyId,
      indicatorId,
      startDate: '2026-08-01',
      endDate: '2026-08-31',
    });

    const request = httpTesting.expectOne(
      candidate =>
        candidate.url === '/api/measurements'
        && candidate.params.get('company_id') === companyId
        && candidate.params.get('indicator_id') === indicatorId
        && candidate.params.get('start_date') === '2026-08-01'
        && candidate.params.get('end_date') === '2026-08-31',
    );

    expect(request.request.method).toBe('GET');

    request.flush([
      measurementResponse,
    ]);

    await expect(resultPromise).resolves.toEqual([
      {
        id: measurementResponse.id,
        indicatorId,
        referenceDate:
          measurementResponse.reference_date,
        actualValue: 125.5,
        observation:
          measurementResponse.observation,
        createdBy:
          measurementResponse.created_by,
        createdAt:
          measurementResponse.created_at,
        updatedAt:
          measurementResponse.updated_at,
      },
    ]);
  });

  it('should normalize and create a measurement', async () => {
    const resultPromise = repository.create(input);

    const request =
      httpTesting.expectOne('/api/measurements');

    expect(request.request.method).toBe('POST');

    expect(request.request.body).toEqual({
      indicator_id: indicatorId,
      reference_date: '2026-08-20',
      actual_value: 125.5,
      observation: 'Valor conferido.',
    });

    request.flush(measurementResponse);

    await expect(resultPromise).resolves.toMatchObject({
      indicatorId,
      referenceDate: '2026-08-20',
      actualValue: 125.5,
      observation: 'Valor conferido.',
    });
  });

  it('should update and delete a measurement', async () => {
    const updatePromise = repository.update(
      measurementResponse.id,
      input,
    );

    const updateRequest =
      httpTesting.expectOne(
        `/api/measurements/${measurementResponse.id}`,
      );

    expect(updateRequest.request.method).toBe('PUT');

    updateRequest.flush(measurementResponse);

    await updatePromise;

    const deletePromise = repository.delete(
      measurementResponse.id,
    );

    const deleteRequest =
      httpTesting.expectOne(
        `/api/measurements/${measurementResponse.id}`,
      );

    expect(deleteRequest.request.method).toBe('DELETE');

    deleteRequest.flush(null);

    await expect(deletePromise).resolves.toBeUndefined();
  });

});