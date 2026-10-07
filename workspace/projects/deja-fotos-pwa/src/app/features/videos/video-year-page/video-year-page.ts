import {
  ChangeDetectionStrategy,
  Component,
  HostListener,
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
  duration_seconds: number | null;
}

interface MediaListResponse {
  items: readonly MediaResponse[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

interface VideoViewItem {
  id: string;
  originalDate: string | null;
  originalName: string;
  durationSeconds: number | null;
  posterUrl: string | null;
}

const PAGE_SIZE = 30;

@Component({
  selector: 'app-video-year-page',
  standalone: true,
  templateUrl: './video-year-page.html',
  styleUrl: './video-year-page.scss',
  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class VideoYearPageComponent
  implements OnInit, OnDestroy {
  private readonly http =
    inject(HttpClient);

  private readonly route =
    inject(ActivatedRoute);

  private readonly router =
    inject(Router);

  private readonly objectUrls =
    new Set<string>();

  private currentPage = 0;

  private totalPages = 0;

  readonly year =
    signal<number | null>(null);

  readonly videos =
    signal<readonly VideoViewItem[]>([]);

  readonly loading =
    signal(true);

  readonly loadingMore =
    signal(false);

  readonly hasMore =
    signal(false);

  readonly error =
    signal<string | null>(null);

  readonly loadMoreError =
    signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    const yearParam =
      this.route.snapshot.paramMap.get(
        'year',
      );

    const selectedYear =
      Number(yearParam);

    if (
      !yearParam
      || !Number.isInteger(selectedYear)
      || selectedYear < 1
      || selectedYear > 9999
    ) {
      this.error.set(
        'Ano inválido.',
      );

      this.loading.set(false);

      return;
    }

    this.year.set(selectedYear);

    try {
      await this.loadPage(
        1,
        false,
      );
    } catch {
      this.error.set(
        'Não foi possível carregar os vídeos.',
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

  @HostListener('window:scroll')
  onWindowScroll(): void {
    const documentElement =
      document.documentElement;

    const remaining =
      documentElement.scrollHeight
      - window.innerHeight
      - window.scrollY;

    if (remaining <= 400) {
      void this.loadNextPage();
    }
  }

  goBack(): void {
    void this.router.navigateByUrl(
      '/videos',
    );
  }

  openVideo(
    mediaId: string,
  ): void {
    const selectedYear =
      this.year();

    if (selectedYear === null) {
      return;
    }

    void this.router.navigate(
      [
        '/videos',
        selectedYear,
        'media',
        mediaId,
      ],
    );
  }

  async loadNextPage(): Promise<void> {
    if (
      this.loading()
      || this.loadingMore()
      || !this.hasMore()
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
        'Não foi possível carregar mais vídeos.',
      );
    } finally {
      this.loadingMore.set(false);
    }
  }

  private async loadPage(
    page: number,
    append: boolean,
  ): Promise<void> {
    const selectedYear =
      this.year();

    if (selectedYear === null) {
      throw new Error(
        'Ano inválido.',
      );
    }

    const response =
      await firstValueFrom(
        this.http.get<
          MediaListResponse
        >(
          '/api/fotos/media',
          {
            params: {
              media_type:
                'video',
              original_year:
                selectedYear,
              page,
              page_size:
                PAGE_SIZE,
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

    if (append) {
      this.videos.update(
        current => [
          ...current,
          ...items,
        ],
      );
    } else {
      this.videos.set(items);
    }

    this.currentPage =
      response.page;

    this.totalPages =
      response.total_pages;

    this.hasMore.set(
      this.currentPage
      < this.totalPages,
    );
  }

  private async createViewItem(
    item: MediaResponse,
  ): Promise<VideoViewItem> {
    let posterUrl:
      string | null = null;

    try {
      const poster =
        await firstValueFrom(
          this.http.get(
            `/api/fotos/media/${item.id}/poster`,
            {
              responseType:
                'blob',
            },
          ),
        );

      posterUrl =
        URL.createObjectURL(
          poster,
        );

      this.objectUrls.add(
        posterUrl,
      );
    } catch {
      posterUrl = null;
    }

    return {
      id: item.id,
      originalDate:
        item.original_date,
      originalName:
        item.original_name,
      durationSeconds:
        item.duration_seconds,
      posterUrl,
    };
  }
}