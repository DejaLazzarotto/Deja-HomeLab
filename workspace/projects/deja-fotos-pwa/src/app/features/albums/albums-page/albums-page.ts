import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  signal,
} from '@angular/core';

import {
  HttpClient,
} from '@angular/common/http';

import {
  firstValueFrom,
} from 'rxjs';

interface AlbumResponse {
  id: string;
  organization_id: string;
  tenant_id: string;
  environment_id: string;
  name: string;
  description: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
}

@Component({
  selector: 'app-albums-page',
  standalone: true,
  templateUrl: './albums-page.html',
  styleUrl: './albums-page.scss',
  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class AlbumsPageComponent
  implements OnInit {
  private readonly http =
    inject(HttpClient);

  readonly albums =
    signal<readonly AlbumResponse[]>([]);

  readonly loading =
    signal(true);

  readonly error =
    signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    try {
      const albums =
        await firstValueFrom(
          this.http.get<
            readonly AlbumResponse[]
          >(
            '/api/fotos/albums',
          ),
        );

      this.albums.set(
        albums.filter(
          album => album.active,
        ),
      );
    } catch {
      this.error.set(
        'Não foi possível carregar os álbuns.',
      );
    } finally {
      this.loading.set(false);
    }
  }
}