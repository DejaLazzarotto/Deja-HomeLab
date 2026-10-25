import { describe, expect, it } from 'vitest';

import { shuffleTracks } from './shuffle-tracks';

describe('shuffleTracks', () => {
  it('mantém todas as faixas sem repetição', () => {
    const tracks = ['musica-1', 'musica-2', 'musica-3', 'musica-4'];

    const result = shuffleTracks(tracks, () => 0);

    expect(result).toHaveLength(tracks.length);
    expect(new Set(result).size).toBe(tracks.length);
    expect(result).toEqual(expect.arrayContaining(tracks));
  });

  it('não modifica a lista original', () => {
    const tracks = ['musica-1', 'musica-2', 'musica-3'];

    shuffleTracks(tracks, () => 0);

    expect(tracks).toEqual([
      'musica-1',
      'musica-2',
      'musica-3',
    ]);
  });

  it('aceita uma biblioteca vazia', () => {
    expect(shuffleTracks([])).toEqual([]);
  });
});
