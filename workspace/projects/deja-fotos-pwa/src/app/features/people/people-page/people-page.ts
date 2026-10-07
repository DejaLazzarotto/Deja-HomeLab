import {
  ChangeDetectionStrategy,
  Component,
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

  readonly people = signal<readonly PersonViewItem[]>([]);

  readonly loading = signal(true);

  readonly error = signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    try {
      const response = await firstValueFrom(
        this.http.get<PersonListResponse>(
          '/api/fotos/people',
          {
            params: {
              active: true,
              page: 1,
              page_size: PAGE_SIZE,
            },
          },
        ),
      );

      const people = await Promise.all(
        response.items.map(
          (person) => this.createViewItem(person),
        ),
      );

      this.people.set(people);
    } catch {
      this.error.set(
        'Não foi possível carregar as pessoas.',
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

  goBack(): void {
    void this.router.navigateByUrl('/explore');
  }

  openPerson(personId: string): void {
    void this.router.navigate([
      '/people',
      personId,
    ]);
  }

  private async createViewItem(
    person: PersonResponse,
  ): Promise<PersonViewItem> {
    const [avatarUrl, mediaCount] =
      await Promise.all([
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
          `/api/fotos/people/${person.id}/avatar`,
          {
            responseType: 'blob',
          },
        ),
      );

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
          `/api/fotos/people/${personId}/media`,
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