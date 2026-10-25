import { TestBed } from '@angular/core/testing';
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest';

import { MusicLibraryService } from './music-library.service';
import { MusicPlayerService } from './music-player.service';

describe('MusicPlayerService', () => {
  let service: MusicPlayerService;
  let library: {
    listTracks: ReturnType<typeof vi.fn>;
    loadTrack: ReturnType<typeof vi.fn>;
  };

  beforeEach(() => {
    vi.spyOn(HTMLMediaElement.prototype, 'play')
      .mockResolvedValue(undefined);
    vi.spyOn(HTMLMediaElement.prototype, 'pause')
      .mockImplementation(() => undefined);
    vi.spyOn(HTMLMediaElement.prototype, 'load')
      .mockImplementation(() => undefined);

    vi.spyOn(URL, 'createObjectURL')
      .mockReturnValue('blob:vivaro-test');
    vi.spyOn(URL, 'revokeObjectURL')
      .mockImplementation(() => undefined);

    library = {
      listTracks: vi.fn().mockResolvedValue(['primeira.mp3']),
      loadTrack: vi.fn().mockResolvedValue(
        new Blob(['audio'], { type: 'audio/mpeg' }),
      ),
    };

    TestBed.configureTestingModule({
      providers: [
        MusicPlayerService,
        { provide: MusicLibraryService, useValue: library },
      ],
    });

    service = TestBed.inject(MusicPlayerService);
  });

  afterEach(() => {
    service.stop();
    TestBed.resetTestingModule();
    vi.restoreAllMocks();
  });

  it('carrega e reproduz uma música pela biblioteca', async () => {
    await service.initialize();

    expect(library.listTracks).toHaveBeenCalledOnce();
    expect(library.loadTrack).toHaveBeenCalledWith('primeira.mp3');
    expect(HTMLMediaElement.prototype.play).toHaveBeenCalledOnce();
    expect(service.error()).toBeNull();
  });

  it('permite pausar a reprodução', async () => {
    await service.initialize();
    service.pause();

    expect(HTMLMediaElement.prototype.pause).toHaveBeenCalled();
    expect(service.isPlaying()).toBe(false);
  });

  it('libera a URL temporária ao interromper', async () => {
    await service.initialize();
    service.stop();

    expect(URL.revokeObjectURL).toHaveBeenCalledWith(
      'blob:vivaro-test',
    );
    expect(service.isPlaying()).toBe(false);
  });

  it('não reproduz quando a biblioteca está vazia', async () => {
    library.listTracks.mockResolvedValue([]);

    await service.initialize();

    expect(library.loadTrack).not.toHaveBeenCalled();
    expect(HTMLMediaElement.prototype.play).not.toHaveBeenCalled();
    expect(service.isPlaying()).toBe(false);
  });

  it('não inicia a música após Pause durante o carregamento', async () => {
    let finish!: (blob: Blob) => void;

    library.loadTrack.mockReturnValue(
      new Promise<Blob>((resolve) => {
        finish = resolve;
      }),
    );

    const initialization = service.initialize();

    await vi.waitFor(() => {
      expect(library.loadTrack).toHaveBeenCalledOnce();
    });

    service.pause();

    finish(new Blob(['audio'], { type: 'audio/mpeg' }));

    await initialization;

    expect(HTMLMediaElement.prototype.play).not.toHaveBeenCalled();
    expect(service.isPlaying()).toBe(false);
  });
  it('retoma a faixa após Pause durante o carregamento', async () => {
    let finish!: (blob: Blob) => void;

    library.loadTrack.mockReturnValueOnce(
      new Promise<Blob>((resolve) => {
        finish = resolve;
      }),
    );

    const initialization = service.initialize();

    await vi.waitFor(() => {
      expect(library.loadTrack).toHaveBeenCalledOnce();
    });

    service.pause();
    finish(new Blob(['audio'], { type: 'audio/mpeg' }));
    await initialization;

    await service.play();

    expect(library.loadTrack).toHaveBeenCalledTimes(2);
    expect(library.loadTrack).toHaveBeenNthCalledWith(
      2,
      'primeira.mp3',
    );
    expect(HTMLMediaElement.prototype.play).toHaveBeenCalledOnce();
  });
  it('não devolve uma faixa antiga à fila após trocar de álbum', async () => {
    let finishOld!: (blob: Blob) => void;

    library.listTracks
      .mockResolvedValueOnce(['antiga.mp3'])
      .mockResolvedValueOnce(['nova.mp3']);

    library.loadTrack.mockImplementation((filename: string) => {
      if (filename === 'antiga.mp3') {
        return new Promise<Blob>((resolve) => {
          finishOld = resolve;
        });
      }

      return Promise.resolve(
        new Blob(['nova'], { type: 'audio/mpeg' }),
      );
    });

    const oldInitialization = service.initialize();

    await vi.waitFor(() => {
      expect(library.loadTrack).toHaveBeenCalledWith('antiga.mp3');
    });

    await service.initialize();

    finishOld(new Blob(['antiga'], { type: 'audio/mpeg' }));
    await oldInitialization;

    expect(service['queue']).not.toContain('antiga.mp3');
    expect(service['tracks']).toEqual(['nova.mp3']);
  });
  it('não duplica faixas após Play e Pause rápidos', async () => {
    const pending: Array<(blob: Blob) => void> = [];

    library.listTracks.mockResolvedValue(['primeira.mp3', 'segunda.mp3']);

    library.loadTrack.mockImplementation(
      () => new Promise<Blob>((resolve) => {
        pending.push(resolve);
      }),
    );

    const initialization = service.initialize();

    await vi.waitFor(() => {
      expect(pending).toHaveLength(1);
    });

    service.pause();
    const resumed = service.play();

    await vi.waitFor(() => {
      expect(pending).toHaveLength(2);
    });

    pending[0](new Blob(['antiga'], { type: 'audio/mpeg' }));
    await initialization;

    pending[1](new Blob(['atual'], { type: 'audio/mpeg' }));
    await resumed;

    expect(new Set(service['queue']).size).toBe(service['queue'].length);
    expect(HTMLMediaElement.prototype.play).toHaveBeenCalledOnce();
  });
  it('pausa durante o vídeo e retoma somente quando permitido', async () => {
    await service.initialize();

    service['audio'].dispatchEvent(new Event('play'));

    expect(service.isPlaying()).toBe(true);

    service.pauseForVideo();

    expect(HTMLMediaElement.prototype.pause).toHaveBeenCalled();
    expect(service.isPlaying()).toBe(false);

    const callsBeforeResume = vi.mocked(
      HTMLMediaElement.prototype.play,
    ).mock.calls.length;

    service.resumeFromVideo();

    await vi.waitFor(() => {
      expect(HTMLMediaElement.prototype.play).toHaveBeenCalledTimes(
        callsBeforeResume + 1,
      );
    });

    service.pauseForVideo();
    service.pause();

    const callsAfterManualPause = vi.mocked(
      HTMLMediaElement.prototype.play,
    ).mock.calls.length;

    service.resumeFromVideo();

    expect(HTMLMediaElement.prototype.play).toHaveBeenCalledTimes(
      callsAfterManualPause,
    );
  });
  it('não inicia a música se o álbum foi encerrado durante a consulta', async () => {
    let finish!: (tracks: string[]) => void;

    library.listTracks.mockReturnValue(
      new Promise<string[]>((resolve) => {
        finish = resolve;
      }),
    );

    const initialization = service.initialize();

    service.stop();
    finish(['primeira.mp3']);

    await initialization;

    expect(library.loadTrack).not.toHaveBeenCalled();
    expect(HTMLMediaElement.prototype.play).not.toHaveBeenCalled();
  });
});
