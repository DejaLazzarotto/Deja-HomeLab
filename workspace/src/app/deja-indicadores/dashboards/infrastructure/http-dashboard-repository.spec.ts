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
  HttpDashboardRepository,
} from './http-dashboard-repository';

describe('HttpDashboardRepository', () => {

  let repository: HttpDashboardRepository;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    repository = new HttpDashboardRepository(
      TestBed.inject(HttpClient),
    );

    httpTesting =
      TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('should request and map the dashboard overview', async () => {
    const resultPromise = repository.getOverview({
      companyId: 'company-id',
      startDate: '2026-08-01',
      endDate: '2026-08-31',
    });

    const request = httpTesting.expectOne(
      item =>
        item.url === '/api/dashboards/overview',
    );

    expect(request.request.method).toBe('GET');

    expect(
      request.request.params.get('company_id'),
    ).toBe('company-id');

    expect(
      request.request.params.get('start_date'),
    ).toBe('2026-08-01');

    expect(
      request.request.params.get('end_date'),
    ).toBe('2026-08-31');

    request.flush({
      totals: {
        companies: 1,
        indicators: 1,
        measurements: 2,
      },
      companies_by_status: [
        {
          status: 'active',
          count: 1,
        },
      ],
      indicators_by_status: [
        {
          status: 'active',
          count: 1,
        },
      ],
      indicators: [
        {
          id: 'indicator-id',
          company_id: 'company-id',
          company_trade_name: 'Empresa Teste',
          name: 'Faturamento',
          unit: 'R$',
          direction: 'higher_is_better',
          status: 'active',
          target_value: '100.5000',
          current_measurement: {
            id: 'measurement-id',
            reference_date: '2026-08-20',
            actual_value: '110.2500',
            observation: null,
          },
          achievement_percentage: '109.7015',
          situation: 'on_target',
          history: [
            {
              id: 'measurement-id',
              reference_date: '2026-08-20',
              actual_value: '110.2500',
              observation: null,
            },
          ],
        },
      ],
    });

    await expect(resultPromise).resolves.toEqual({
      totals: {
        companies: 1,
        indicators: 1,
        measurements: 2,
      },
      companiesByStatus: [
        {
          status: 'active',
          count: 1,
        },
      ],
      indicatorsByStatus: [
        {
          status: 'active',
          count: 1,
        },
      ],
      indicators: [
        {
          id: 'indicator-id',
          companyId: 'company-id',
          companyTradeName: 'Empresa Teste',
          name: 'Faturamento',
          unit: 'R$',
          direction: 'higher_is_better',
          status: 'active',
          targetValue: 100.5,
          currentMeasurement: {
            id: 'measurement-id',
            referenceDate: '2026-08-20',
            actualValue: 110.25,
            observation: '',
          },
          achievementPercentage: 109.7015,
          situation: 'on_target',
          history: [
            {
              id: 'measurement-id',
              referenceDate: '2026-08-20',
              actualValue: 110.25,
              observation: '',
            },
          ],
        },
      ],
    });
  });

});