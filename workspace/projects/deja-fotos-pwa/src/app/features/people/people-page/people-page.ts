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

interface PersonResponse {
  id: string;
  name: string;
  description: string | null;
  active: boolean;
  avatar_content_type: string | null;
}

interface PersonListResponse {
  items: readonly PersonResponse[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

interface PersonMediaListResponse {
  items: readonly unknown[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

interface PersonViewItem extends PersonResponse {
  avatarUrl: string | null;
  mediaCount: number;
}

const PAGE_SIZE = 30;
const DETAIL_BATCH_SIZE = 5;

@Component({
  selector: 'app-people-page',
  standalone: true,
  templateUrl: './people-page.html',
  styleUrl: './people-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PeoplePageComponent implements OnInit, OnDestroy {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly objectUrls = new Set<string>();

  private currentPage = 0;
  private totalPages = 1;
  private destroyed = false;

  readonly people = signal<readonly PersonViewItem[]>([]);
  readonly loading = signal(true);
  readonly loadingMore = signal(false);
  readonly hasMore = signal(false);
  readonly error = signal<string | null>(null);
  readonly loadMoreError = signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    await this.loadNextPage();
  }

  @HostListener('window:scroll')
  onScroll(): void {
    if (
      this.destroyed ||
      this.loading() ||
      this.loadingMore() ||
      !this.hasMore() ||
      this.loadMoreError()
    ) {
      return;
    }

    const remaining =
      document.documentElement.scrollHeight -
      window.innerHeight -
      window.scrollY;

    if (remaining < 500) {
      void this.loadNextPage();
    }
  }

  async loadNextPage(): Promise<void> {
    if (this.destroyed || this.loadingMore()) {
      return;
    }

    const nextPage = this.currentPage + 1;

    if (nextPage > this.totalPages) {
      return;
    }

    this.loadingMore.set(true);
    this.loadMoreError.set(null);

    try {
      const response = await firstValueFrom(
        this.http.get<PersonListResponse>(
          '/api/fotos/people',
          {
            params: {
              active: true,
              page: nextPage,
              page_size: PAGE_SIZE,
            },
          },
        ),
      );

      if (this.destroyed) {
        return;
      }

      const newPeople: PersonViewItem[] = [];

      for (
        let index = 0;
        index < response.items.length;
        index += DETAIL_BATCH_SIZE
      ) {
        const batch = response.items.slice(
          index,
          index + DETAIL_BATCH_SIZE,
        );

        const items = await Promise.all(
          batch.map((person) => this.createViewItem(person)),
        );

        if (this.destroyed) {
          return;
        }

        newPeople.push(...items);
      }

      const existingIds = new Set(
        this.people().map((person) => person.id),
      );

      this.people.update((existing) => [
        ...existing,
        ...newPeople.filter(
          (person) => !existingIds.has(person.id),
        ),
      ]);

      this.currentPage = response.page;
      this.totalPages = response.total_pages;
      this.hasMore.set(this.currentPage < this.totalPages);
      this.error.set(null);
    } catch {
      if (this.currentPage === 0) {
        this.error.set(
          'Não foi possível carregar as pessoas.',
        );
      } else {
        this.loadMoreError.set(
          'Não foi possível carregar mais pessoas.',
        );
      }
    } finally {
      this.loading.set(false);
      this.loadingMore.set(false);
    }
  }

  ngOnDestroy(): void {
    this.destroyed = true;

    for (const objectUrl of this.objectUrls) {
      URL.revokeObjectURL(objectUrl);
    }

    this.objectUrls.clear();
  }

  goBack(): void {
    void this.router.navigateByUrl('/explore');
  }

  openPerson(personId: string): void {
    void this.router.navigate(['/people', personId]);
  }

  private async createViewItem(
    person: PersonResponse,
  ): Promise<PersonViewItem> {
    const [avatarUrl, mediaCount] = await Promise.all([
      this.loadAvatar(person),
      this.loadMediaCount(person.id),
    ]);

    return {
      ...person,
      avatarUrl,
      mediaCount,
    };
  }

  private async loadAvatar(
    person: PersonResponse,
  ): Promise<string | null> {
    if (!person.avatar_content_type) {
      return null;
    }

    try {
      const blob = await firstValueFrom(
        this.http.get(
          '/api/fotos/people/' + person.id + '/avatar',
          { responseType: 'blob' },
        ),
      );

      if (this.destroyed) {
        return null;
      }

      const objectUrl = URL.createObjectURL(blob);
      this.objectUrls.add(objectUrl);

      return objectUrl;
    } catch {
      return null;
    }
  }

  private async loadMediaCount(
    personId: string,
  ): Promise<number> {
    try {
      const response = await firstValueFrom(
        this.http.get<PersonMediaListResponse>(
          '/api/fotos/people/' + personId + '/media',
          {
            params: {
              page: 1,
              page_size: 1,
            },
          },
        ),
      );

      return response.total;
    } catch {
      return 0;
    }
  }
}
