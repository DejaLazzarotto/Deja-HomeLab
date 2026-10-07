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

export interface VideoYearSummary {
  year: number;
  mediaCount: number;
}

@Component({
  selector: 'app-videos-page',
  standalone: true,
  templateUrl: './videos-page.html',
  styleUrl: './videos-page.scss',
  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class VideosPageComponent
  implements OnInit {
  private readonly http =
    inject(HttpClient);

  private readonly router =
    inject(Router);

  readonly years =
    signal<readonly VideoYearSummary[]>([]);

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
            {
              params: {
                media_type: 'video',
              },
            },
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
        'Não foi possível carregar os vídeos.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  openYear(year: number): void {
    void this.router.navigate(
      [
        '/videos',
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