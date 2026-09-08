export interface ClientUserLink {
  readonly id: string;
  readonly userId: string;
  readonly clientId: string;
  readonly createdAt: string;
}

export interface ClientUserLinkCreate {
  readonly userId: string;
  readonly clientId: string;
}

export interface ClientUserLinkUpdate {
  readonly clientId: string;
}