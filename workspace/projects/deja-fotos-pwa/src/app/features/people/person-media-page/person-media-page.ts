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
interface MediaPeriod {
  year: number | null;
  month: number | null;
  media_count: number;
}
interface PeriodItem {
  key: string;
  label: string;
  count: number;
}
interface MediaViewItem extends MediaResponse {
  thumbnailUrl: string | null;
}

const PAGE_SIZE = 30;
const MONTH_NAMES = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
];

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

  readonly personId = signal<string | null>(null);
  readonly person = signal<PersonResponse | null>(null);
  readonly media = signal<readonly MediaViewItem[]>([]);
  readonly periods = signal<readonly MediaPeriod[]>([]);
  readonly choices = signal<readonly PeriodItem[]>([]);
  readonly mode = signal<'years' | 'months' | 'grid'>('years');
  readonly selectedYear = signal<number | null>(null);
  readonly selectedMonth = signal<number | null>(null);
  readonly undated = signal(false);
  readonly allPhotos = signal(false);
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
    const yearValue = this.route.snapshot.paramMap.get('year');
    const monthValue = this.route.snapshot.paramMap.get('month');
    const all = this.route.snapshot.routeConfig?.path?.endsWith('/all') ?? false;
    this.allPhotos.set(all);
    try {
      const person = await firstValueFrom(
        this.http.get<PersonResponse>(`/api/fotos/people/${personId}`),
      );
      this.person.set(person);
      if (all) {
        this.mode.set('grid');
        await this.loadPage(1, false);
      } else if (yearValue === 'undated' && monthValue === 'undated') {
        this.undated.set(true);
        this.mode.set('grid');
        await this.loadPage(1, false);
      } else if (yearValue !== null) {
        const year = Number(yearValue);
        if (!Number.isInteger(year) || year < 1 || year > 9999) {
          throw new Error('Ano inválido.');
        }
        this.selectedYear.set(year);
        if (monthValue !== null) {
          const month = Number(monthValue);
          if (!Number.isInteger(month) || month < 1 || month > 12) {
            throw new Error('Mês inválido.');
          }
          this.selectedMonth.set(month);
          this.mode.set('grid');
          await this.loadPage(1, false);
        } else {
          await this.loadPeriods();
          this.mode.set('months');
          this.choices.set(
            this.periods().filter(period => period.year === year && period.month !== null)
              .map(period => ({
                key: String(period.month),
                label: MONTH_NAMES[(period.month ?? 1) - 1],
                count: period.media_count,
              })).sort((a, b) => Number(b.key) - Number(a.key)),
          );
          this.total.set(this.choices().reduce((sum, period) => sum + period.count, 0));
        }
      } else {
        await this.loadPeriods();
        this.mode.set('years');
        const byYear = new Map<number, number>();
        for (const period of this.periods()) {
          if (period.year !== null) {
            byYear.set(period.year, (byYear.get(period.year) ?? 0) + period.media_count);
          }
        }
        this.choices.set([
          ...[...byYear.entries()].sort((a, b) => b[0] - a[0]).map(([year, count]) => ({
            key: String(year), label: String(year), count,
          })),
          ...(() => {
            const count = this.periods().filter(period => period.year === null)
              .reduce((sum, period) => sum + period.media_count, 0);
            return count ? [{ key: 'undated', label: 'Sem data', count }] : [];
          })(),
        ]);
        this.total.set(this.periods().reduce((sum, period) => sum + period.media_count, 0));
      }
    } catch {
      this.error.set('Não foi possível carregar as mídias desta pessoa.');
    } finally {
      this.loading.set(false);
    }
  }

  ngOnDestroy(): void {
    for (const objectUrl of this.objectUrls) URL.revokeObjectURL(objectUrl);
    this.objectUrls.clear();
  }

  private async loadPeriods(): Promise<void> {
    this.periods.set(await firstValueFrom(
      this.http.get<readonly MediaPeriod[]>(
        `/api/fotos/people/${this.personId()}/media/periods`,
      ),
    ));
  }

  @HostListener('window:scroll')
  onWindowScroll(): void {
    if (this.mode() !== 'grid') return;
    const remaining = document.documentElement.scrollHeight - window.innerHeight - window.scrollY;
    if (remaining <= 400) void this.loadNextPage();
  }

  goBack(): void {
    const id = this.personId();
    if (!id) return;
    if (this.mode() === 'grid' && !this.allPhotos()) {
      void this.router.navigate(this.undated() ? ['/people', id] : ['/people', id, 'period', this.selectedYear()]);
    } else if (this.mode() === 'months' || this.allPhotos()) {
      void this.router.navigate(['/people', id]);
    } else {
      void this.router.navigateByUrl('/people');
    }
  }

  openPeriod(key: string): void {
    const id = this.personId();
    if (!id) return;
    if (this.mode() === 'years') {
      void this.router.navigate(
        key === 'undated' ? ['/people', id, 'period', 'undated', 'undated'] : ['/people', id, 'period', key],
      );
    } else {
      void this.router.navigate(['/people', id, 'period', this.selectedYear(), key]);
    }
  }

  openAllPhotos(): void {
    const id = this.personId();
    if (id) void this.router.navigate(['/people', id, 'all']);
  }

  openMedia(mediaId: string): void {
    const id = this.personId();
    if (!id) return;
    if (this.allPhotos()) {
      void this.router.navigate(['/people', id, 'media', mediaId]);
    } else {
      void this.router.navigate([
        '/people', id, 'period',
        this.undated() ? 'undated' : this.selectedYear(),
        this.undated() ? 'undated' : this.selectedMonth(),
        'media', mediaId,
      ]);
    }
  }

  async loadNextPage(): Promise<void> {
    if (this.loading() || this.loadingMore() || !this.hasMore()) return;
    this.loadingMore.set(true);
    this.loadMoreError.set(null);
    try {
      await this.loadPage(this.currentPage + 1, true);
    } catch {
      this.loadMoreError.set('Não foi possível carregar mais mídias.');
    } finally {
      this.loadingMore.set(false);
    }
  }

  private async loadPage(page: number, append: boolean): Promise<void> {
    const id = this.personId();
    if (!id) throw new Error('Pessoa inválida.');
    const params: Record<string, string | number | boolean> = {
      page, page_size: PAGE_SIZE,
    };
    if (this.undated()) params['without_date'] = true;
    else if (!this.allPhotos() && this.selectedYear() !== null) {
      params['year'] = this.selectedYear()!;
      if (this.selectedMonth() !== null) params['month'] = this.selectedMonth()!;
    }
    const response = await firstValueFrom(
      this.http.get<PersonMediaListResponse>(`/api/fotos/people/${id}/media`, { params }),
    );
    const items = await Promise.all(response.items.map(item => this.createViewItem(item)));
    if (append) this.media.update(current => [...current, ...items]);
    else this.media.set(items);
    this.currentPage = response.page;
    this.totalPages = response.total_pages;
    this.total.set(response.total);
    this.hasMore.set(this.currentPage < this.totalPages);
  }

  private async createViewItem(item: MediaResponse): Promise<MediaViewItem> {
    let thumbnailUrl: string | null = null;
    try {
      const derivative = item.media_type === 'video' ? 'poster' : 'thumbnail';
      const blob = await firstValueFrom(
        this.http.get(`/api/fotos/media/${item.id}/${derivative}`, { responseType: 'blob' }),
      );
      thumbnailUrl = URL.createObjectURL(blob);
      this.objectUrls.add(thumbnailUrl);
    } catch {
      thumbnailUrl = null;
    }
    return { ...item, thumbnailUrl };
  }
}
