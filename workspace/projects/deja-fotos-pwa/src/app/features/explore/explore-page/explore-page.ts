
import {
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  OnInit,
  inject,
  signal,
} from '@angular/core';

import { HttpClient } from '@angular/common/http';

import {
  Router,
} from '@angular/router';

import { firstValueFrom } from 'rxjs';

import {
  AuthenticationService,
} from '../../../core/authentication/authentication.service';

interface PersonResponse {
  readonly id: string;
  readonly name: string;
  readonly avatar_content_type: string | null;
}

interface PersonListResponse {
  readonly items: readonly PersonResponse[];
  readonly page: number;
  readonly page_size: number;
  readonly total: number;
  readonly total_pages: number;
}

interface PersonPreview extends PersonResponse {
  readonly avatarUrl: string | null;
}

@Component({
  selector: 'app-explore-page',
  standalone: true,
  templateUrl: './explore-page.html',
  styleUrl: './explore-page.scss',
  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class ExplorePageComponent
implements OnInit, OnDestroy {
  private readonly http =
    inject(HttpClient);

  private readonly router =
    inject(Router);

  private readonly authentication =
    inject(AuthenticationService);

  private readonly objectUrls =
    new Set<string>();

  readonly peoplePreview =
    signal<readonly PersonPreview[]>([]);

  readonly profileMenuOpen =
    signal(false);

  readonly currentUser =
    this.authentication.user;

  get userInitial(): string {
    return this.currentUser()
      ?.name
      ?.trim()
      .charAt(0)
      .toUpperCase() || '?';
  }

  toggleProfileMenu(): void {
    this.profileMenuOpen.update(open => !open);
  }

  closeProfileMenu(): void {
    this.profileMenuOpen.set(false);
  }

  logout(): void {
    this.closeProfileMenu();
    this.authentication.logout();

    void this.router.navigateByUrl('/login');
  }

  async ngOnInit(): Promise<void> {
    try {
      const response = await firstValueFrom(
        this.http.get<PersonListResponse>(
          '/api/fotos/people',
          {
            params: {
              active: true,
              page: 1,
              page_size: 30,
            },
          },
        ),
      );

      const selected = [...response.items]
        .sort((left, right) => {
          const avatarPriority =
            Number(Boolean(right.avatar_content_type))
            - Number(Boolean(left.avatar_content_type));

          if (avatarPriority !== 0) {
            return avatarPriority;
          }

          return left.name.localeCompare(
            right.name,
            'pt-BR',
          );
        })
        .slice(0, 4);

      const preview = await Promise.all(
        selected.map(
          person => this.createPersonPreview(person),
        ),
      );

      this.peoplePreview.set(preview);
    } catch {
      this.peoplePreview.set([]);
    }
  }

  ngOnDestroy(): void {
    for (const url of this.objectUrls) {
      URL.revokeObjectURL(url);
    }

    this.objectUrls.clear();
  }

  openDates(): void {
    void this.router.navigateByUrl(
      '/dates',
    );
  }

  openPeople(): void {
    void this.router.navigateByUrl(
      '/people',
    );
  }

  openPerson(
    personId: string,
  ): void {
    void this.router.navigate([
      '/people',
      personId,
    ]);
  }

  openAlbums(): void {
    void this.router.navigateByUrl(
      '/albums',
    );
  }

  openRecents(): void {
    void this.router.navigateByUrl('/recent');
  }
  openVideos(): void {
    void this.router.navigateByUrl(
      '/videos',
    );
  }

  private async createPersonPreview(
    person: PersonResponse,
  ): Promise<PersonPreview> {
    return {
      ...person,
      avatarUrl:
        await this.loadAvatar(person),
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

      const url =
        URL.createObjectURL(blob);

      this.objectUrls.add(url);

      return url;
    } catch {
      return null;
    }
  }
}
