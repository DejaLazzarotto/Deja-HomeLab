import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';

import { firstValueFrom } from 'rxjs';

export interface FavoriteStatusResponse {
  media_id: string;
  is_favorite: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class FavoritesService {
  private readonly http = inject(HttpClient);

  async isFavorite(mediaId: string): Promise<boolean> {
    const response = await firstValueFrom(
      this.http.get<FavoriteStatusResponse>(
        `/api/fotos/favorites/${encodeURIComponent(mediaId)}`,
      ),
    );

    return response.is_favorite;
  }

  async add(mediaId: string): Promise<void> {
    await firstValueFrom(
      this.http.put<FavoriteStatusResponse>(
        `/api/fotos/favorites/${encodeURIComponent(mediaId)}`,
        {},
      ),
    );
  }

  async remove(mediaId: string): Promise<void> {
    await firstValueFrom(
      this.http.delete<void>(
        `/api/fotos/favorites/${encodeURIComponent(mediaId)}`,
      ),
    );
  }
}