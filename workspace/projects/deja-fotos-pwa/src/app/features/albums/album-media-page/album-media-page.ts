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

interface AlbumResponse {
  readonly id: string;
  readonly name: string;
}

interface MediaResponse {
  readonly id: string;
  readonly media_type: 'image' | 'video';
  readonly original_date: string | null;
  readonly original_name: string;
}

interface MediaListResponse {
  readonly items: readonly MediaResponse[];
  readonly page: number;
  readonly page_size: number;
  readonly total: number;
  readonly total_pages: number;
}

interface MediaViewItem {
  readonly id: string;
  readonly mediaType: 'image' | 'video';
  readonly originalDate: string | null;
  readonly originalName: string;
  readonly thumbnailUrl: string | null;
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
  selector: 'app-album-media-page',
  standalone: true,
  templateUrl: './album-media-page.html',
  styleUrl: './album-media-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AlbumMediaPageComponent
  implements OnInit, OnDestroy {

  private readonly http = inject(HttpClient);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  private readonly objectUrls = new Set<string>();

  private currentPage = 0;
  private totalPages = 0;
  private destroyed = false;

  readonly albumId = signal<string | null>(null);
  readonly albumName = signal('');

  readonly year = signal<number | null>(null);
  readonly month = signal<number | null>(null);
  readonly monthName = signal('');

  readonly media = signal<readonly MediaViewItem[]>([]);

  readonly loading = signal(true);
  readonly loadingMore = signal(false);
  readonly hasMore = signal(false);

  readonly error = signal<string | null>(null);
  readonly loadMoreError = signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    const albumId =
      this.route.snapshot.paramMap.get('albumId');

    const yearParam =
      this.route.snapshot.paramMap.get('year');

    const monthParam =
      this.route.snapshot.paramMap.get('month');

    const selectedYear = Number(yearParam);
    const selectedMonth = Number(monthParam);

    if (
      !albumId ||
      !yearParam ||
      !monthParam ||
      !Number.isInteger(selectedYear) ||
      !Number.isInteger(selectedMonth) ||
      selectedYear < 1 ||
      selectedYear > 9999 ||
      selectedMonth < 1 ||
      selectedMonth > 12
    ) {
      this.error.set('Álbum ou período inválido.');
      this.loading.set(false);
      return;
    }

    this.albumId.set(albumId);
    this.year.set(selectedYear);
    this.month.set(selectedMonth);
    this.monthName.set(MONTH_NAMES[selectedMonth - 1]);

    try {
      const album = await firstValueFrom(
        this.http.get<AlbumResponse>(
          `/api/fotos/albums/${albumId}`,
        ),
      );

      if (this.destroyed) {
        return;
      }

      this.albumName.set(album.name);

      await this.loadPage(1, false);
    } catch {
      if (!this.destroyed) {
        this.error.set(
          'Não foi possível carregar as mídias deste álbum.',
        );
      }
    } finally {
      if (!this.destroyed) {
        this.loading.set(false);
      }
    }
  }

  ngOnDestroy(): void {
    this.destroyed = true;

    for (const url of this.objectUrls) {
      URL.revokeObjectURL(url);
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
    const albumId = this.albumId();
    const year = this.year();

    if (!albumId || year === null) {
      void this.router.navigateByUrl('/albums');
      return;
    }

    void this.router.navigate([
      '/albums',
      albumId,
      year,
    ]);
  }

  openMedia(mediaId: string): void {
    const albumId = this.albumId();
    const year = this.year();
    const month = this.month();

    if (!albumId || year === null || month === null) {
      return;
    }

    void this.router.navigate([
      '/albums',
      albumId,
      year,
      month,
      'media',
      mediaId,
    ]);
  }

  async loadNextPage(): Promise<void> {
    if (
      this.destroyed ||
      this.loading() ||
      this.loadingMore() ||
      !this.hasMore()
    ) {
      return;
    }

    this.loadingMore.set(true);
    this.loadMoreError.set(null);

    try {
      await this.loadPage(this.currentPage + 1, true);
    } catch {
      if (!this.destroyed) {
        this.loadMoreError.set(
          'Não foi possível carregar mais mídias.',
        );
      }
    } finally {
      if (!this.destroyed) {
        this.loadingMore.set(false);
      }
    }
  }

  private async loadPage(
    page: number,
    append: boolean,
  ): Promise<void> {
    const albumId = this.albumId();
    const year = this.year();
    const month = this.month();

    if (!albumId || year === null || month === null) {
      throw new Error('Álbum ou período inválido.');
    }

    const response = await firstValueFrom(
      this.http.get<MediaListResponse>(
        '/api/fotos/media',
        {
          params: {
            album_id: albumId,
            original_year: year,
            original_month: month,
            page,
            page_size: PAGE_SIZE,
          },
        },
      ),
    );

    if (this.destroyed) {
      return;
    }

    const items = await Promise.all(
      response.items.map(
        item => this.createViewItem(item),
      ),
    );

    if (this.destroyed) {
      return;
    }

    if (append) {
      this.media.update(current => [
        ...current,
        ...items,
      ]);
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

      const blob = await firstValueFrom(
        this.http.get(
          `/api/fotos/media/${item.id}/${derivative}`,
          {
            responseType: 'blob',
          },
        ),
      );

      if (!this.destroyed) {
        thumbnailUrl = URL.createObjectURL(blob);
        this.objectUrls.add(thumbnailUrl);
      }
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