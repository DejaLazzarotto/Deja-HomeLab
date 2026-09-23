/*
 * Deja Fotos
 *
 * Serviço de cadastro e organização de pessoas.
 */

import {
  Person,
  PersonFilters,
  PersonInput,
  PersonPage,
  PersonRepository,
} from '../domain/person';

const MAX_AVATAR_SIZE_BYTES =
  10 * 1024 * 1024;

const AVATAR_TYPES = new Set([
  'image/jpeg',
  'image/png',
  'image/webp',
]);

export class PersonService {
  constructor(
    private readonly repository: PersonRepository,
  ) {}

  list(
    filters: PersonFilters = {},
  ): Promise<PersonPage> {
    return this.repository.list(filters);
  }

  create(input: PersonInput): Promise<Person> {
    return this.repository.create(
      this.validate(input),
    );
  }

  update(
    id: string,
    input: PersonInput,
  ): Promise<Person> {
    return this.repository.update(
      id,
      this.validate(input),
    );
  }

  delete(id: string): Promise<void> {
    return this.repository.delete(id);
  }

  loadAvatar(id: string): Promise<Blob> {
    return this.repository.loadAvatar(id);
  }

  uploadAvatar(
    id: string,
    file: File,
  ): Promise<Person> {
    if (
      file.size === 0
      || !AVATAR_TYPES.has(file.type)
    ) {
      throw new Error(
        'Selecione uma imagem JPEG, PNG ou WebP.',
      );
    }

    if (file.size > MAX_AVATAR_SIZE_BYTES) {
      throw new Error(
        'O avatar deve ter no máximo 10 MB.',
      );
    }

    return this.repository.uploadAvatar(
      id,
      file,
    );
  }

  removeAvatar(id: string): Promise<Person> {
    return this.repository.removeAvatar(id);
  }

  linkMedia(
    personId: string,
    mediaId: string,
  ): Promise<void> {
    return this.repository.linkMedia(
      personId,
      mediaId,
    );
  }

  unlinkMedia(
    personId: string,
    mediaId: string,
  ): Promise<void> {
    return this.repository.unlinkMedia(
      personId,
      mediaId,
    );
  }

  private validate(
    input: PersonInput,
  ): PersonInput {
    const environmentId =
      input.environmentId.trim();
    const name = input.name.trim();
    const description =
      input.description?.trim() || null;

    if (!environmentId) {
      throw new Error(
        'Selecione o ambiente da pessoa.',
      );
    }

    if (!name || name.length > 150) {
      throw new Error(
        'Informe um nome de até 150 caracteres.',
      );
    }

    if (
      description
      && description.length > 5000
    ) {
      throw new Error(
        'As observações devem ter no máximo 5000 caracteres.',
      );
    }

    return {
      environmentId,
      name,
      description,
      active: input.active,
    };
  }
}