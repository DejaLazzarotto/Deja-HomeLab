import {
  ChangeDetectionStrategy,
  Component,
  HostListener,
  OnDestroy,
  OnInit,
  inject,
  signal,
} from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { ActivatedRoute, Router } from '@angular/router';

import { firstValueFrom } from 'rxjs';

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

const PAGE_SIZE = 30;

@Component({
  selector: 'app-month-page',
  standalone: true,
  templateUrl: './month-page.html',
  styleUrl: './month-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MonthPageComponent implements OnInit, OnDestroy {
  private readonly http = inject(HttpClient);

  private readonly route = inject(ActivatedRoute);

  private readonly router = inject(Router);

  private readonly objectUrls = new Set<string>();

  private currentPage = 0;

  private totalPages = 0;

  readonly year = signal<number | null>(null);

  readonly month = signal<number | null>(null);

  readonly monthName = signal<string>('');

  readonly media = signal<readonly MediaViewItem[]>([]);

  readonly loading = signal(true);

  readonly loadingMore = signal(false);

  readonly hasMore = signal(false);

  readonly error = signal<string | null>(null);

  readonly loadMoreError = signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    const yearParam = this.route.snapshot.paramMap.get('year');

    const monthParam = this.route.snapshot.paramMap.get('month');

    const selectedYear = Number(yearParam);

    const selectedMonth = Number(monthParam);

    if (
      !yearParam ||
      !monthParam ||
      !Number.isInteger(selectedYear) ||
      !Number.isInteger(selectedMonth) ||
      selectedYear < 1 ||
      selectedYear > 9999 ||
      selectedMonth < 1 ||
      selectedMonth > 12
    ) {
      this.error.set('Período inválido.');

      this.loading.set(false);

      return;
    }

    this.year.set(selectedYear);
    this.month.set(selectedMonth);
    this.monthName.set(MONTH_NAMES[selectedMonth - 1]);

    try {
      await this.loadPage(1, false);
    } catch {
      this.error.set('Não foi possível carregar as mídias.');
    } finally {
      this.loading.set(false);
    }
  }

  ngOnDestroy(): void {
    for (const objectUrl of this.objectUrls) {
      URL.revokeObjectURL(objectUrl);
    }

    this.objectUrls.clear();
  }

  @HostListener('window:scroll')
  onWindowScroll(): void {
    const documentElement = document.documentElement;

    const remaining =
      documentElement.scrollHeight -
      window.innerHeight -
      window.scrollY;

    if (remaining <= 400) {
      void this.loadNextPage();
    }
  }

  goBack(): void {
    const selectedYear = this.year();

    if (selectedYear === null) {
      void this.router.navigateByUrl('/dates');

      return;
    }

    void this.router.navigate(['/dates', selectedYear]);
  }

  openMedia(mediaId: string): void {
    const selectedYear = this.year();

    const selectedMonth = this.month();

    if (selectedYear === null || selectedMonth === null) {
      return;
    }

    void this.router.navigate([
      '/dates',
      selectedYear,
      selectedMonth,
      'media',
      mediaId,
    ]);
  }

  async loadNextPage(): Promise<void> {
    if (
      this.loading() ||
      this.loadingMore() ||
      !this.hasMore()
    ) {
      return;
    }

    this.loadingMore.set(true);
    this.loadMoreError.set(null);

    try {
      await this.loadPage(
        this.currentPage + 1,
        true,
      );
    } catch {
      this.loadMoreError.set(
        'Não foi possível carregar mais mídias.',
      );
    } finally {
      this.loadingMore.set(false);
    }
  }

  private async loadPage(
    page: number,
    append: boolean,
  ): Promise<void> {
    const selectedYear = this.year();

    const selectedMonth = this.month();

    if (
      selectedYear === null ||
      selectedMonth === null
    ) {
      throw new Error('Período inválido.');
    }

    const response = await firstValueFrom(
      this.http.get<MediaListResponse>(
        '/api/fotos/media',
        {
          params: {
            original_year: selectedYear,
            original_month: selectedMonth,
            page,
            page_size: PAGE_SIZE,
          },
        },
      ),
    );

    const items = await Promise.all(
      response.items.map(
        (item) => this.createViewItem(item),
      ),
    );

    if (append) {
      this.media.update(
        (current) => [
          ...current,
          ...items,
        ],
      );
    } else {
      this.media.set(items);
    }

    this.currentPage = response.page;

    this.totalPages = response.total_pages;

    this.hasMore.set(
      this.currentPage < this.totalPages,
    );
  }

  private async createViewItem(
    item: MediaResponse,
  ): Promise<MediaViewItem> {
    let thumbnailUrl: string | null = null;

    try {
      const derivative =
        item.media_type === 'video'
          ? 'poster'
          : 'thumbnail';

      const thumbnail = await firstValueFrom(
        this.http.get(
          `/api/fotos/media/${item.id}/${derivative}`,
          {
            responseType: 'blob',
          },
        ),
      );

      thumbnailUrl = URL.createObjectURL(thumbnail);

      this.objectUrls.add(thumbnailUrl);
    } catch {
      thumbnailUrl = null;
    }

    return {
      id: item.id,
      mediaType: item.media_type,
      originalDate: item.original_date,
      originalName: item.original_name,
      thumbnailUrl,
    };
  }
}