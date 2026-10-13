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

import { Router } from '@angular/router';

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

const PAGE_SIZE = 30;

@Component({
  selector: 'app-favorites-page',
  standalone: true,
  templateUrl: './favorites-page.html',
  styleUrl: './favorites-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FavoritesPageComponent implements OnInit, OnDestroy {
  private readonly http = inject(HttpClient);

  private readonly router = inject(Router);

  private readonly objectUrls = new Set<string>();

  private currentPage = 0;

  private totalPages = 0;

  readonly media = signal<readonly MediaViewItem[]>([]);

  readonly loading = signal(true);

  readonly loadingMore = signal(false);

  readonly hasMore = signal(false);

  readonly error = signal<string | null>(null);

  readonly loadMoreError = signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    try {
      await this.loadPage(1, false);
    } catch {
      this.error.set('Não foi possível carregar os favoritos.');
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
    void this.router.navigateByUrl('/explore');
  }

  openMedia(mediaId: string): void {
    void this.router.navigate(['/favorites', 'media', mediaId]);
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
    const response = await firstValueFrom(
      this.http.get<MediaListResponse>(
        '/api/fotos/favorites',
        {
          params: {
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