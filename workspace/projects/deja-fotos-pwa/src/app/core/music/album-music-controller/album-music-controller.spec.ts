import { TestBed } from '@angular/core/testing';
import { NavigationEnd, Router } from '@angular/router';
import { Subject } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { MusicPlayerService } from '../music-player.service';
import { AlbumMusicController } from './album-music-controller';

describe('AlbumMusicController', () => {
  const events = new Subject<NavigationEnd>();

  const router = {
    url: '/albums',
    events: events.asObservable(),
  };

  const player = {
    initialize: vi.fn().mockResolvedValue(undefined),
    stop: vi.fn(),
  };

  let controller: AlbumMusicController;

  function navigate(url: string): void {
    router.url = url;
    events.next(new NavigationEnd(1, url, url));
  }

  beforeEach(() => {
    router.url = '/albums';
    vi.clearAllMocks();

    TestBed.configureTestingModule({
      providers: [
        AlbumMusicController,
        { provide: Router, useValue: router },
        { provide: MusicPlayerService, useValue: player },
      ],
    });

    controller = TestBed.inject(AlbumMusicController);
  });

  it('não inicia música na lista Meus álbuns', () => {
    expect(controller.activeAlbumId()).toBeNull();
    expect(player.initialize).not.toHaveBeenCalled();
  });

  it('inicia música ao abrir um álbum', () => {
    navigate('/albums/10');

    expect(controller.activeAlbumId()).toBe('10');
    expect(player.initialize).toHaveBeenCalledOnce();
  });

  it('mantém a reprodução durante a navegação interna', () => {
    navigate('/albums/10');
    navigate('/albums/10/2026');
    navigate('/albums/10/2026/10');
    navigate('/albums/10/2026/10/media/123');

    expect(player.initialize).toHaveBeenCalledOnce();
    expect(player.stop).not.toHaveBeenCalled();
  });

  it('interrompe a música ao sair do álbum', () => {
    navigate('/albums/10');
    navigate('/albums');

    expect(controller.activeAlbumId()).toBeNull();
    expect(player.stop).toHaveBeenCalledOnce();
  });

  it('reinicia a reprodução ao trocar de álbum', () => {
    navigate('/albums/10');
    navigate('/albums/20');

    expect(controller.activeAlbumId()).toBe('20');
    expect(player.initialize).toHaveBeenCalledTimes(2);
  });
});
