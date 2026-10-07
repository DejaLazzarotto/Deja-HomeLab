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

      await this.loadPage(1, false);
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
    void this.router.navigateByUrl('/people');
  }

  openMedia(mediaId: string): void {
    const personId = this.personId();

    if (!personId) {
      return;
    }

    void this.router.navigate([
      '/people',
      personId,
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