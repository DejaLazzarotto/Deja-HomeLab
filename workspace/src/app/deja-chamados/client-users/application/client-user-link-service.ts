import {
  ClientUserLink,
  ClientUserLinkCreate,
  ClientUserLinkUpdate,
} from '../domain/client-user-link';

import {
  HttpClientUserLinkRepository,
} from '../infrastructure/http-client-user-link-repository';

export class ClientUserLinkService {

  constructor(
    private readonly repository: HttpClientUserLinkRepository,
  ) {}

  findByUserId(
    userId: string,
  ): Promise<ClientUserLink | undefined> {
    return this.repository.findByUserId(
      userId,
    );
  }

  create(
    input: ClientUserLinkCreate,
  ): Promise<ClientUserLink> {
    return this.repository.create(
      input,
    );
  }

  update(
    userId: string,
    input: ClientUserLinkUpdate,
  ): Promise<ClientUserLink> {
    return this.repository.update(
      userId,
      input,
    );
  }

  delete(
    userId: string,
  ): Promise<void> {
    return this.repository.delete(
      userId,
    );
  }

}