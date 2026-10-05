import {
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
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

interface MediaResponse {
  id: string;
  media_type: 'image' | 'video';
  original_date: string | null;
  original_name: string;
}

interface MediaListResponse {
  items: readonly MediaResponse[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

interface MediaViewItem {
  id: string;
  mediaType: 'image' | 'video';
  originalDate: string | null;
  originalName: string;
  thumbnailUrl: string | null;
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
  selector: 'app-month-page',
  standalone: true,
  templateUrl: './month-page.html',
  styleUrl: './month-page.scss',
  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class MonthPageComponent
  implements OnInit, OnDestroy {
  private readonly http =
    inject(HttpClient);

  private readonly route =
    inject(ActivatedRoute);

  private readonly router =
    inject(Router);

  private readonly objectUrls =
    new Set<string>();

  readonly year =
    signal<number | null>(null);

  readonly month =
    signal<number | null>(null);

  readonly monthName =
    signal<string>('');

  readonly media =
    signal<readonly MediaViewItem[]>([]);

  readonly loading =
    signal(true);

  readonly error =
    signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    const yearParam =
      this.route.snapshot.paramMap.get(
        'year',
      );

    const monthParam =
      this.route.snapshot.paramMap.get(
        'month',
      );

    const selectedYear =
      Number(yearParam);

    const selectedMonth =
      Number(monthParam);

    if (
      !yearParam
      || !monthParam
      || !Number.isInteger(selectedYear)
      || !Number.isInteger(selectedMonth)
      || selectedYear < 1
      || selectedYear > 9999
      || selectedMonth < 1
      || selectedMonth > 12
    ) {
      this.error.set(
        'Período inválido.',
      );

      this.loading.set(false);

      return;
    }

    this.year.set(selectedYear);
    this.month.set(selectedMonth);
    this.monthName.set(
      MONTH_NAMES[
        selectedMonth - 1
      ],
    );

    try {
      const response =
        await firstValueFrom(
          this.http.get<MediaListResponse>(
            '/api/fotos/media',
            {
              params: {
                original_year:
                  selectedYear,
                original_month:
                  selectedMonth,
                page: 1,
                page_size: 200,
              },
            },
          ),
        );

      const items =
        await Promise.all(
          response.items.map(
            item =>
              this.createViewItem(
                item,
              ),
          ),
        );

      this.media.set(items);
    } catch {
      this.error.set(
        'Não foi possível carregar as mídias.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  ngOnDestroy(): void {
    for (
      const objectUrl
      of this.objectUrls
    ) {
      URL.revokeObjectURL(
        objectUrl,
      );
    }

    this.objectUrls.clear();
  }

  goBack(): void {
    const selectedYear =
      this.year();

    if (selectedYear === null) {
      void this.router.navigateByUrl(
        '/dates',
      );

      return;
    }

    void this.router.navigate(
      [
        '/dates',
        selectedYear,
      ],
    );
  }

  private async createViewItem(
    item: MediaResponse,
  ): Promise<MediaViewItem> {
    let thumbnailUrl: string | null =
      null;

    try {
      const thumbnail =
        await firstValueFrom(
          this.http.get(
            `/api/fotos/media/${item.id}/thumbnail`,
            {
              responseType: 'blob',
            },
          ),
        );

      thumbnailUrl =
        URL.createObjectURL(
          thumbnail,
        );

      this.objectUrls.add(
        thumbnailUrl,
      );
    } catch {
      thumbnailUrl = null;
    }

    return {
      id: item.id,
      mediaType: item.media_type,
      originalDate:
        item.original_date,
      originalName:
        item.original_name,
      thumbnailUrl,
    };
  }
}