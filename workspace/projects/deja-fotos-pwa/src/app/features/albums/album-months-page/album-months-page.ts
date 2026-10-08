import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  signal,
} from '@angular/core';

import { HttpClient } from '@angular/common/http';

import {
  ActivatedRoute,
  Router,
} from '@angular/router';

import { firstValueFrom } from 'rxjs';

interface AlbumResponse {
  readonly id: string;
  readonly name: string;
}

interface AlbumPeriodResponse {
  readonly year: number | null;
  readonly month: number | null;
  readonly media_count: number;
  readonly description: string | null;
}

interface AlbumMonthSummary {
  readonly month: number;
  readonly name: string;
  readonly mediaCount: number;
  readonly description: string | null;
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
  selector: 'app-album-months-page',
  standalone: true,
  templateUrl: './album-months-page.html',
  styleUrl: './album-months-page.scss',
  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class AlbumMonthsPageComponent
  implements OnInit {

  private readonly http = inject(HttpClient);

  private readonly route = inject(ActivatedRoute);

  private readonly router = inject(Router);

  readonly albumId = signal<string | null>(null);

  readonly albumName = signal('');

  readonly year = signal<number | null>(null);

  readonly months =
    signal<readonly AlbumMonthSummary[]>([]);

  readonly loading = signal(true);

  readonly error = signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    const albumId =
      this.route.snapshot.paramMap.get('albumId');

    const yearParam =
      this.route.snapshot.paramMap.get('year');

    const selectedYear = Number(yearParam);

    if (
      !albumId ||
      !yearParam ||
      !Number.isInteger(selectedYear) ||
      selectedYear < 1 ||
      selectedYear > 9999
    ) {
      this.error.set('Álbum ou ano inválido.');
      this.loading.set(false);
      return;
    }

    this.albumId.set(albumId);
    this.year.set(selectedYear);

    try {
      const [album, periods] = await Promise.all([
        firstValueFrom(
          this.http.get<AlbumResponse>(
            `/api/fotos/albums/${albumId}`,
          ),
        ),
        firstValueFrom(
          this.http.get<
            readonly AlbumPeriodResponse[]
          >(
            `/api/fotos/albums/${albumId}/periods`,
          ),
        ),
      ]);

      this.albumName.set(album.name);

      this.months.set(
        periods
          .filter(
            period =>
              period.year === selectedYear &&
              period.month !== null &&
              period.month >= 1 &&
              period.month <= 12,
          )
          .map(period => ({
            month: period.month!,
            name: MONTH_NAMES[period.month! - 1],
            mediaCount: period.media_count,
            description: period.description,
          }))
          .sort(
            (left, right) =>
              right.month - left.month,
          ),
      );
    } catch {
      this.error.set(
        'Não foi possível carregar os meses do álbum.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  openMonth(month: number): void {
    const albumId = this.albumId();
    const year = this.year();

    if (!albumId || year === null) {
      return;
    }

    void this.router.navigate([
      '/albums',
      albumId,
      year,
      month,
    ]);
  }

  goBack(): void {
    const albumId = this.albumId();

    if (!albumId) {
      void this.router.navigateByUrl('/albums');
      return;
    }

    void this.router.navigate([
      '/albums',
      albumId,
    ]);
  }
}