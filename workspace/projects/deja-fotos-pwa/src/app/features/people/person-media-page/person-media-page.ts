import {
  ChangeDetectionStrategy,
  Component,
  HostListener,
  OnDestroy,
  OnInit,
  inject,
  signal,
} from '@angular/core';

import { HttpClient, HttpParams } from '@angular/common/http';
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
  name: string;
  mediaCount: number;
}

interface MediaViewItem extends MediaResponse {
  thumbnailUrl: string | null;
}

type PersonView = 'years' | 'months' | 'media';

const PAGE_SIZE = 30;

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
  selector: 'app-person-media-page',
  standalone: true,
  templateUrl: './person-media-page.html',
  styleUrl: './person-media-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PersonMediaPageComponent implements OnInit, OnDestroy {
  private readonly http = inject(HttpClient);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  private readonly objectUrls = new Set<string>();

  private currentPage = 0;
  private totalPages = 0;
  private requestVersion = 0;
  private destroyed = false;

  readonly personId = signal<string | null>(null);
  readonly person = signal<PersonResponse | null>(null);

  readonly view = signal<PersonView>('years');
  readonly periods = signal<readonly PersonMediaPeriodResponse[]>([]);
  readonly years = signal<readonly PersonYearSummary[]>([]);
  readonly months = signal<readonly PersonMonthSummary[]>([]);

  readonly selectedYear = signal<number | null>(null);
  readonly selectedMonth = signal<number | null>(null);
  readonly withoutDate = signal(false);
  readonly undatedCount = signal(0);

  readonly media = signal<readonly MediaViewItem[]>([]);
  readonly total = signal(0);

  readonly loading = signal(true);
  readonly loadingMore = signal(false);
  readonly hasMore = signal(false);
  readonly error = signal<string | null>(null);
  readonly loadMoreError = signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    const personId = this.route.snapshot.paramMap.get('personId');

    if (!personId) {
      this.error.set('Pessoa inválida.');
      this.loading.set(false);
      return;
    }

    this.personId.set(personId);

    try {
      const person = await firstValueFrom(
        this.http.get<PersonResponse>(`/api/fotos/people/${personId}`),
      );

      if (this.destroyed) return;

      this.person.set(person);

      const periods = await firstValueFrom(
        this.http.get<readonly PersonMediaPeriodResponse[]>(
          `/api/fotos/people/${personId}/media/periods`,
        ),
      );

      if (this.destroyed) return;

      this.periods.set(periods);
      this.prepareYears(periods);
      await this.restoreSelection();
    } catch {
      if (!this.destroyed) {
        this.error.set('Não foi possível carregar os períodos desta pessoa.');
      }
    } finally {
      if (!this.destroyed) this.loading.set(false);
    }
  }

  ngOnDestroy(): void {
    this.destroyed = true;
    this.requestVersion += 1;
    this.releaseThumbnails();
  }

  private prepareYears(
    periods: readonly PersonMediaPeriodResponse[],
  ): void {
    const totals = new Map<number, number>();
    let undated = 0;
    let total = 0;

    for (const period of periods) {
      total += period.media_count;

      if (period.year === null || period.month === null) {
        undated += period.media_count;
        continue;
      }

      totals.set(
        period.year,
        (totals.get(period.year) ?? 0) + period.media_count,
      );
    }

    this.total.set(total);
    this.undatedCount.set(undated);

    this.years.set(
      Array.from(totals, ([year, mediaCount]) => ({
        year,
        mediaCount,
      })).sort((a, b) => b.year - a.year),
    );
  }

  private prepareMonths(year: number): void {
    this.months.set(
      this.periods()
        .filter(
          (period) =>
            period.year === year &&
            period.month !== null &&
            period.month >= 1 &&
            period.month <= 12,
        )
        .map((period) => ({
          month: period.month as number,
          name: MONTH_NAMES[(period.month as number) - 1],
          mediaCount: period.media_count,
        }))
        .sort((a, b) => b.month - a.month),
    );
  }

  private async restoreSelection(): Promise<void> {
    const params = this.route.snapshot.queryParamMap;
    const yearValue = params?.get('year');
    const monthValue = params?.get('month');
    const undated = params?.get('without_date') === 'true';

    if (undated && this.undatedCount() > 0) {
      await this.openUndated();
      return;
    }

    if (yearValue === null || yearValue === undefined) return;

    const year = Number(yearValue);
    if (!Number.isInteger(year) || !this.years().some(x => x.year === year)) {
      return;
    }

    this.openYear(year);

    if (monthValue === null || monthValue === undefined) return;

    const month = Number(monthValue);
    if (!Number.isInteger(month) || !this.months().some(x => x.month === month)) {
      return;
    }

    await this.openMonth(month);
  }

  openYear(year: number): void {
    if (!this.years().some((item) => item.year === year)) return;

    this.requestVersion += 1;
    this.releaseThumbnails();
    this.media.set([]);
    this.hasMore.set(false);

    this.selectedYear.set(year);
    this.selectedMonth.set(null);
    this.withoutDate.set(false);
    this.prepareMonths(year);

    this.error.set(null);
    this.loadMoreError.set(null);
    this.view.set('months');
    this.updateUrl();
    window.scrollTo(0, 0);
  }

  async openMonth(month: number): Promise<void> {
    if (
      this.selectedYear() === null ||
      !this.months().some((item) => item.month === month)
    ) {
      return;
    }

    this.selectedMonth.set(month);
    this.withoutDate.set(false);

    await this.enterMedia();
  }

  async openUndated(): Promise<void> {
    if (this.undatedCount() === 0) return;

    this.selectedYear.set(null);
    this.selectedMonth.set(null);
    this.withoutDate.set(true);

    await this.enterMedia();
  }

  private async enterMedia(): Promise<void> {
    const version = ++this.requestVersion;

    this.releaseThumbnails();
    this.media.set([]);
    this.currentPage = 0;
    this.totalPages = 0;
    this.hasMore.set(false);

    this.error.set(null);
    this.loadMoreError.set(null);
    this.view.set('media');
    this.loading.set(true);
    this.updateUrl();
    window.scrollTo(0, 0);

    try {
      await this.loadPage(1, false, version);
    } catch {
      if (version === this.requestVersion && !this.destroyed) {
        this.error.set('Não foi possível carregar as mídias deste período.');
      }
    } finally {
      if (version === this.requestVersion && !this.destroyed) {
        this.loading.set(false);
      }
    }
  }

  @HostListener('window:scroll')
  onWindowScroll(): void {
    if (this.view() !== 'media') return;

    const remaining =
      document.documentElement.scrollHeight -
      window.innerHeight -
      window.scrollY;

    if (remaining <= 400) {
      void this.loadNextPage();
    }
  }

  goBack(): void {
    if (this.view() === 'media') {
      this.requestVersion += 1;
      this.releaseThumbnails();
      this.media.set([]);
      this.hasMore.set(false);
      this.error.set(null);

      if (this.withoutDate()) {
        this.selectedYear.set(null);
        this.selectedMonth.set(null);
        this.withoutDate.set(false);
        this.view.set('years');
      } else {
        this.selectedMonth.set(null);
        this.view.set('months');
      }

      this.updateUrl();
      window.scrollTo(0, 0);
      return;
    }

    if (this.view() === 'months') {
      this.selectedYear.set(null);
      this.selectedMonth.set(null);
      this.months.set([]);
      this.view.set('years');
      this.updateUrl();
      window.scrollTo(0, 0);
      return;
    }

    void this.router.navigateByUrl('/people');
  }

  openMedia(mediaId: string): void {
    const personId = this.personId();
    if (!personId) return;

    void this.router.navigate(
      ['/people', personId, 'media', mediaId],
      { queryParams: this.periodParams() },
    );
  }

  async loadNextPage(): Promise<void> {
    if (
      this.view() !== 'media' ||
      this.loading() ||
      this.loadingMore() ||
      !this.hasMore()
    ) {
      return;
    }

    const version = this.requestVersion;
    this.loadingMore.set(true);
    this.loadMoreError.set(null);

    try {
      await this.loadPage(this.currentPage + 1, true, version);
    } catch {
      if (version === this.requestVersion && !this.destroyed) {
        this.loadMoreError.set('Não foi possível carregar mais mídias.');
      }
    } finally {
      this.loadingMore.set(false);
    }
  }

  private async loadPage(
    page: number,
    append: boolean,
    version: number,
  ): Promise<void> {
    const personId = this.personId();
    if (!personId) throw new Error('Pessoa inválida.');

    let params = new HttpParams()
      .set('page', page)
      .set('page_size', PAGE_SIZE);

    const year = this.selectedYear();
    const month = this.selectedMonth();

    if (this.withoutDate()) {
      params = params.set('without_date', true);
    } else if (year !== null && month !== null) {
      params = params.set('year', year).set('month', month);
    } else {
      throw new Error('Período inválido.');
    }

    const response = await firstValueFrom(
      this.http.get<PersonMediaListResponse>(
        `/api/fotos/people/${personId}/media`,
        { params },
      ),
    );

    if (version !== this.requestVersion || this.destroyed) return;

    const items = await Promise.all(
      response.items.map((item) => this.createViewItem(item, version)),
    );

    if (version !== this.requestVersion || this.destroyed) {
      for (const item of items) {
        if (item.thumbnailUrl) {
          URL.revokeObjectURL(item.thumbnailUrl);
          this.objectUrls.delete(item.thumbnailUrl);
        }
      }
      return;
    }

    if (append) {
      this.media.update((current) => [...current, ...items]);
    } else {
      this.media.set(items);
    }

    this.currentPage = response.page;
    this.totalPages = response.total_pages;
    this.hasMore.set(this.currentPage < this.totalPages);
  }

  private async createViewItem(
    item: MediaResponse,
    version: number,
  ): Promise<MediaViewItem> {
    let thumbnailUrl: string | null = null;

    try {
      const derivative =
        item.media_type === 'video' ? 'poster' : 'thumbnail';

      const blob = await firstValueFrom(
        this.http.get(
          `/api/fotos/media/${item.id}/${derivative}`,
          { responseType: 'blob' },
        ),
      );

      if (version === this.requestVersion && !this.destroyed) {
        thumbnailUrl = URL.createObjectURL(blob);
        this.objectUrls.add(thumbnailUrl);
      }
    } catch {
      thumbnailUrl = null;
    }

    return { ...item, thumbnailUrl };
  }

  private releaseThumbnails(): void {
    for (const url of this.objectUrls) {
      URL.revokeObjectURL(url);
    }

    this.objectUrls.clear();
  }

  private periodParams(): Record<string, string | number | boolean> {
    if (this.withoutDate()) {
      return { without_date: true };
    }

    const year = this.selectedYear();
    const month = this.selectedMonth();

    if (year === null) return {};
    if (month === null) return { year };

    return { year, month };
  }

  private updateUrl(): void {
    const personId = this.personId();
    if (!personId) return;

    void this.router.navigate(
      ['/people', personId],
      {
        queryParams: this.periodParams(),
        replaceUrl: true,
      },
    );
  }
}