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

interface PersonResponse {
  id: string;
  name: string;
  description: string | null;
  active: boolean;
  avatar_content_type: string | null;
}

interface MediaResponse {
  id: string;
  media_type: 'image' | 'video';
  original_date: string | null;
  original_name: string;
}

interface PersonMediaListResponse {
  items: readonly MediaResponse[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

interface PersonMediaPeriodResponse {
  year: number | null;
  month: number | null;
  media_count: number;
}

interface PersonYearSummary {
  year: number;
  mediaCount: number;
}

interface PersonMonthSummary {
  month: number;
  mediaCount: number;
}
interface MediaViewItem extends MediaResponse {
  thumbnailUrl: string | null;
}

const PAGE_SIZE = 30;

@Component({
  selector: 'app-person-media-page',
  standalone: true,
  templateUrl: './person-media-page.html',
  styleUrl: './person-media-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PersonMediaPageComponent
  implements OnInit, OnDestroy
{
  private readonly http = inject(HttpClient);

  private readonly route = inject(ActivatedRoute);

  private readonly router = inject(Router);

  private readonly objectUrls = new Set<string>();

  private currentPage = 0;

  private totalPages = 0;

  readonly view = signal<'years' | 'months' | 'media'>('years');

  readonly periods = signal<readonly PersonMediaPeriodResponse[]>([]);

  readonly years = signal<readonly PersonYearSummary[]>([]);

  readonly months = signal<readonly PersonMonthSummary[]>([]);

  readonly selectedYear = signal<number | null>(null);

  readonly selectedMonth = signal<number | null>(null);

  readonly withoutDate = signal(false);

  readonly undatedCount = signal(0);
  readonly personId = signal<string | null>(null);

  readonly person = signal<PersonResponse | null>(null);

  readonly media = signal<readonly MediaViewItem[]>([]);

  readonly total = signal(0);

  readonly loading = signal(true);

  readonly loadingMore = signal(false);

  readonly hasMore = signal(false);

  readonly error = signal<string | null>(null);

  readonly loadMoreError = signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    const personId =
      this.route.snapshot.paramMap.get('personId');

    if (!personId) {
      this.error.set('Pessoa inválida.');
      this.loading.set(false);

      return;
    }

    this.personId.set(personId);

    try {
      const person = await firstValueFrom(
        this.http.get<PersonResponse>(
          `/api/fotos/people/${personId}`,
        ),
      );

      this.person.set(person);

      await this.loadPeriods();
      await this.restoreSelectedPeriod();
    } catch {
      this.error.set(
        'Não foi possível carregar as mídias desta pessoa.',
      );
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
    const documentElement =
      document.documentElement;

    const remaining =
      documentElement.scrollHeight -
      window.innerHeight -
      window.scrollY;

    if (remaining <= 400) {
      void this.loadNextPage();
    }
  }

  goBack(): void {
    if (this.view() === 'media') {
      this.media.set([]);
      this.hasMore.set(false);
      this.loadMoreError.set(null);
      this.error.set(null);

      if (this.withoutDate()) {
        this.withoutDate.set(false);
        this.view.set('years');
      } else {
        this.view.set('months');
      }

      this.total.set(
        this.periods().reduce(
          (sum, period) => sum + period.media_count,
          0,
        ),
      );

      return;
    }

    if (this.view() === 'months') {
      this.selectedYear.set(null);
      this.selectedMonth.set(null);
      this.view.set('years');
      return;
    }

    void this.router.navigateByUrl('/people');
  }

  monthName(month: number): string {
    const names = [
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
    ];

    return names[month - 1] ?? '';
  }
  openYear(year: number): void {
    const months = this.periods()
      .filter(
        (period) =>
          period.year === year &&
          period.month !== null,
      )
      .map((period) => ({
        month: period.month as number,
        mediaCount: period.media_count,
      }))
      .sort((a, b) => b.month - a.month);

    this.selectedYear.set(year);
    this.selectedMonth.set(null);
    this.withoutDate.set(false);
    this.months.set(months);
    this.view.set('months');
  }
  async openMonth(month: number): Promise<void> {
    if (this.selectedYear() === null) {
      return;
    }

    this.selectedMonth.set(month);
    this.withoutDate.set(false);
    await this.openSelectedPeriod();
  }

  async openWithoutDate(): Promise<void> {
    this.selectedYear.set(null);
    this.selectedMonth.set(null);
    this.withoutDate.set(true);
    await this.openSelectedPeriod();
  }

  private async openSelectedPeriod(): Promise<void> {
    this.media.set([]);
    this.currentPage = 0;
    this.totalPages = 0;
    this.hasMore.set(false);
    this.error.set(null);
    this.loadMoreError.set(null);
    this.view.set('media');
    this.loading.set(true);

    try {
      await this.loadPage(1, false);
    } catch {
      this.error.set(
        'Não foi possível carregar as mídias deste período.',
      );
    } finally {
      this.loading.set(false);
    }
  }
  openMedia(mediaId: string): void {
    const personId = this.personId();

    if (!personId) {
      return;
    }

    void this.router.navigate(
      [
        '/people',
        personId,
        'media',
        mediaId,
      ],
      {
        queryParams: this.withoutDate()
          ? { without_date: true }
          : {
              year: this.selectedYear(),
              month: this.selectedMonth(),
            },
      },
    );
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

  private async restoreSelectedPeriod(): Promise<void> {
    const params = this.route.snapshot.queryParamMap;

    if (!params) {
      return;
    }

    if (params.get('without_date') === 'true') {
      if (this.undatedCount() > 0) {
        await this.openWithoutDate();
      }
      return;
    }

    const yearValue = params.get('year');
    const monthValue = params.get('month');

    if (yearValue === null || monthValue === null) {
      return;
    }

    const year = Number(yearValue);
    const month = Number(monthValue);

    if (
      !Number.isInteger(year) ||
      !Number.isInteger(month) ||
      month < 1 ||
      month > 12
    ) {
      return;
    }

    if (!this.years().some((item) => item.year === year)) {
      return;
    }

    this.openYear(year);

    if (this.months().some((item) => item.month === month)) {
      await this.openMonth(month);
    }
  }
  private async loadPeriods(): Promise<void> {
    const personId = this.personId();

    if (!personId) {
      throw new Error('Pessoa inválida.');
    }

    const periods = await firstValueFrom(
      this.http.get<readonly PersonMediaPeriodResponse[]>(
        `/api/fotos/people/${personId}/media/periods`,
      ),
    );

    this.periods.set(periods);

    const totalsByYear = new Map<number, number>();
    let undated = 0;
    let total = 0;

    for (const period of periods) {
      total += period.media_count;

      if (period.year === null || period.month === null) {
        undated += period.media_count;
        continue;
      }

      totalsByYear.set(
        period.year,
        (totalsByYear.get(period.year) ?? 0) + period.media_count,
      );
    }

    this.years.set(
      Array.from(totalsByYear, ([year, mediaCount]) => ({
        year,
        mediaCount,
      })).sort((a, b) => b.year - a.year),
    );

    this.undatedCount.set(undated);
    this.total.set(total);
    this.view.set('years');
  }
  private async loadPage(
    page: number,
    append: boolean,
  ): Promise<void> {
    const personId = this.personId();

    if (!personId) {
      throw new Error('Pessoa inválida.');
    }

    const response = await firstValueFrom(
      this.http.get<PersonMediaListResponse>(
        `/api/fotos/people/${personId}/media`,
        {
          params: {
            page,
            page_size: PAGE_SIZE,
            ...(this.withoutDate()
              ? { without_date: true }
              : {
                  year: this.selectedYear()!,
                  month: this.selectedMonth()!,
                }),
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

    this.total.set(response.total);

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

      const blob = await firstValueFrom(
        this.http.get(
          `/api/fotos/media/${item.id}/${derivative}`,
          {
            responseType: 'blob',
          },
        ),
      );

      thumbnailUrl =
        URL.createObjectURL(blob);

      this.objectUrls.add(thumbnailUrl);
    } catch {
      thumbnailUrl = null;
    }

    return {
      ...item,
      thumbnailUrl,
    };
  }
}