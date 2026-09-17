/*
 * Deja Fotos
 *
 * Album Validator
 */

import {
  AlbumInput,
} from './album';

export class AlbumValidator {
  validate(
    input: AlbumInput,
  ): AlbumInput {
    const environmentId = input.environmentId.trim();
    const name = input.name.trim();
    const description = input.description?.trim() || null;

    if (environmentId.length !== 36) {
      throw new Error('Selecione um ambiente válido.');
    }

    if (!name) {
      throw new Error('Informe o nome do álbum.');
    }

    if (name.length > 150) {
      throw new Error('O nome do álbum deve possuir no máximo 150 caracteres.');
    }

    if (
      description !== null
      && description.length > 5000
    ) {
      throw new Error('A descrição deve possuir no máximo 5.000 caracteres.');
    }

    return {
      environmentId,
      name,
      description,
      active: input.active,
    };
  }
}