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
  HttpReportRepository,
} from './http-report-repository';

describe('HttpReportRepository', () => {

  let repository: HttpReportRepository;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    repository = new HttpReportRepository(
      TestBed.inject(HttpClient),
    );

    httpTesting =
      TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('should request and map the management report', async () => {
    const resultPromise =
      repository.getManagementReport({
        indicatorId: 'indicator-id',
        startDate: '2026-08-01',
      });

    const request = httpTesting.expectOne(
      item =>
        item.url === '/api/reports/management',
    );

    expect(request.request.method).toBe('GET');

    expect(
      request.request.params.get('indicator_id'),
    ).toBe('indicator-id');

    expect(
      request.request.params.get('start_date'),
    ).toBe('2026-08-01');

    request.flush({
      title: 'Relatório gerencial',
      generated_at: '2026-08-21T10:00:00',
      filters: {
        company_id: null,
        indicator_id: 'indicator-id',
        organization_id: null,
        tenant_id: null,
        environment_id: null,
        start_date: '2026-08-01',
        end_date: null,
      },
      overview: {
        totals: {
          companies: 1,
          indicators: 1,
          measurements: 0,
        },
        companies_by_status: [],
        indicators_by_status: [],
        indicators: [
          {
            id: 'indicator-id',
            company_id: 'company-id',
            company_trade_name: 'Empresa Teste',
            name: 'Disponibilidade',
            unit: '%',
            direction: 'higher_is_better',
            status: 'active',
            target_value: '99.9000',
            current_measurement: null,
            achievement_percentage: null,
            situation: 'no_data',
            history: [],
          },
        ],
      },
    });

    const result = await resultPromise;

    expect(result).toEqual({
      title: 'Relatório gerencial',
      generatedAt: '2026-08-21T10:00:00',
      filters: {
        companyId: null,
        indicatorId: 'indicator-id',
        organizationId: null,
        tenantId: null,
        environmentId: null,
        startDate: '2026-08-01',
        endDate: null,
      },
      overview: {
        totals: {
          companies: 1,
          indicators: 1,
          measurements: 0,
        },
        companiesByStatus: [],
        indicatorsByStatus: [],
        indicators: [
          {
            id: 'indicator-id',
            companyId: 'company-id',
            companyTradeName: 'Empresa Teste',
            name: 'Disponibilidade',
            unit: '%',
            direction: 'higher_is_better',
            status: 'active',
            targetValue: 99.9,
            currentMeasurement: null,
            achievementPercentage: null,
            situation: 'no_data',
            history: [],
          },
        ],
      },
    });
  });

});