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

export interface DateYearSummary {
  year: number;
  mediaCount: number;
}

@Component({
  selector: 'app-dates-page',
  standalone: true,
  templateUrl: './dates-page.html',
  styleUrl: './dates-page.scss',
  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class DatesPageComponent
  implements OnInit {
  private readonly http =
    inject(HttpClient);

  private readonly router =
    inject(Router);

  readonly years =
    signal<readonly DateYearSummary[]>([]);

  readonly loading =
    signal(true);

  readonly error =
    signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    try {
      const periods =
        await firstValueFrom(
          this.http.get<
            readonly MediaPeriodResponse[]
          >(
            '/api/fotos/media/periods',
          ),
        );

      const totalsByYear =
        new Map<number, number>();

      for (const period of periods) {
        totalsByYear.set(
          period.year,
          (
            totalsByYear.get(period.year)
            ?? 0
          ) + period.media_count,
        );
      }

      this.years.set(
        Array.from(
          totalsByYear.entries(),
        )
          .map(
            ([
              year,
              mediaCount,
            ]) => ({
              year,
              mediaCount,
            }),
          )
          .sort(
            (left, right) =>
              right.year - left.year,
          ),
      );
    } catch {
      this.error.set(
        'Não foi possível carregar as datas.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  openYear(year: number): void {
    void this.router.navigate(
      [
        '/dates',
        year,
      ],
    );
  }

  goBack(): void {
    void this.router.navigateByUrl(
      '/explore',
    );
  }
}