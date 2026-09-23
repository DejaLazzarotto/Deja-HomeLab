/*
 * Deja Fotos
 *
 * Pessoas cadastradas em um ambiente.
 */

export interface Person {
  readonly id: string;
  readonly organizationId: string;
  readonly tenantId: string;
  readonly environmentId: string;
  readonly name: string;
  readonly description: string | null;
  readonly active: boolean;
  readonly avatarContentType: string | null;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export interface PersonInput {
  readonly environmentId: string;
  readonly name: string;
  readonly description: string | null;
  readonly active: boolean;
}

export interface PersonFilters {
  readonly organizationId?: string;
  readonly tenantId?: string;
  readonly environmentId?: string;
  readonly active?: boolean;
  readonly name?: string;
  readonly page?: number;
  readonly pageSize?: number;
}

export interface PersonPage {
  readonly items: readonly Person[];
  readonly page: number;
  readonly pageSize: number;
  readonly total: number;
  readonly totalPages: number;
}

export interface PersonRepository {
  list(filters?: PersonFilters): Promise<PersonPage>;

  create(input: PersonInput): Promise<Person>;

  update(
    id: string,
    input: PersonInput,
  ): Promise<Person>;

  delete(id: string): Promise<void>;

  loadAvatar(id: string): Promise<Blob>;

  uploadAvatar(
    id: string,
    file: File,
  ): Promise<Person>;

  removeAvatar(id: string): Promise<Person>;

  linkMedia(
    personId: string,
    mediaId: string,
  ): Promise<void>;

  unlinkMedia(
    personId: string,
    mediaId: string,
  ): Promise<void>;
}