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

interface AlbumYearSummary {
  readonly year: number;
  readonly mediaCount: number;
}

@Component({
  selector: 'app-album-years-page',
  standalone: true,
  templateUrl: './album-years-page.html',
  styleUrl: './album-years-page.scss',
  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class AlbumYearsPageComponent
  implements OnInit {

  private readonly http = inject(HttpClient);

  private readonly route = inject(ActivatedRoute);

  private readonly router = inject(Router);

  readonly albumId = signal<string | null>(null);

  readonly albumName = signal('');

  readonly years =
    signal<readonly AlbumYearSummary[]>([]);

  readonly loading = signal(true);

  readonly error = signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    const albumId =
      this.route.snapshot.paramMap.get('albumId');

    if (!albumId) {
      this.error.set('Álbum inválido.');
      this.loading.set(false);
      return;
    }

    this.albumId.set(albumId);

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

      const totalsByYear = new Map<number, number>();

      for (const period of periods) {
        if (period.year === null) {
          continue;
        }

        totalsByYear.set(
          period.year,
          (totalsByYear.get(period.year) ?? 0)
            + period.media_count,
        );
      }

      this.years.set(
        Array.from(totalsByYear.entries())
          .map(([year, mediaCount]) => ({
            year,
            mediaCount,
          }))
          .sort(
            (left, right) =>
              right.year - left.year,
          ),
      );
    } catch {
      this.error.set(
        'Não foi possível carregar os anos do álbum.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  openYear(year: number): void {
    const albumId = this.albumId();

    if (!albumId) {
      return;
    }

    void this.router.navigate([
      '/albums',
      albumId,
      year,
    ]);
  }

  goBack(): void {
    void this.router.navigateByUrl('/albums');
  }
}