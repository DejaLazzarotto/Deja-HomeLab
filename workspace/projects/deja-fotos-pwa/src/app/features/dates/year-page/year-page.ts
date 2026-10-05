import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  signal,
} from '@angular/core';

import {
  HttpClient,
} from '@angular/common/http';

import {
  ActivatedRoute,
  Router,
} from '@angular/router';

import {
  firstValueFrom,
} from 'rxjs';

interface MediaPeriodResponse {
  year: number;
  month: number;
  media_count: number;
}

export interface MonthSummary {
  month: number;
  name: string;
  mediaCount: number;
}

const MONTH_NAMES = [
  'Janeiro',
  'Fevereiro',
  'Março',
  'Abril',
  'Maio',
  'Junho',
  'Julho',
  'Agosto',
  'Setembro',
  'Outubro',
  'Novembro',
  'Dezembro',
] as const;

@Component({
  selector: 'app-year-page',
  standalone: true,
  templateUrl: './year-page.html',
  styleUrl: './year-page.scss',
  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class YearPageComponent
  implements OnInit {
  private readonly http =
    inject(HttpClient);

  private readonly route =
    inject(ActivatedRoute);

  private readonly router =
    inject(Router);

  readonly year =
    signal<number | null>(null);

  readonly months =
    signal<readonly MonthSummary[]>([]);

  readonly loading =
    signal(true);

  readonly error =
    signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    const yearParam =
      this.route.snapshot.paramMap.get(
        'year',
      );

    const selectedYear =
      Number(yearParam);

    if (
      !yearParam
      || !Number.isInteger(selectedYear)
      || selectedYear < 1
      || selectedYear > 9999
    ) {
      this.error.set(
        'Ano inválido.',
      );

      this.loading.set(false);

      return;
    }

    this.year.set(selectedYear);

    try {
      const periods =
        await firstValueFrom(
          this.http.get<
            readonly MediaPeriodResponse[]
          >(
            '/api/fotos/media/periods',
          ),
        );

      this.months.set(
        periods
          .filter(
            period =>
              period.year
              === selectedYear,
          )
          .map(
            period => ({
              month: period.month,
              name:
                MONTH_NAMES[
                  period.month - 1
                ],
              mediaCount:
                period.media_count,
            }),
          )
          .sort(
            (left, right) =>
              right.month - left.month,
          ),
      );
    } catch {
      this.error.set(
        'Não foi possível carregar os meses.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  openMonth(month: number): void {
    const selectedYear =
      this.year();

    if (selectedYear === null) {
      return;
    }

    void this.router.navigate(
      [
        '/dates',
        selectedYear,
        month,
      ],
    );
  }

  goBack(): void {
    void this.router.navigateByUrl(
      '/dates',
    );
  }
}