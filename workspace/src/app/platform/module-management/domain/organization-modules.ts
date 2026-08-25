import {
  ModuleKey,
} from './module-key';

export interface ModuleCatalogItem {
  readonly key: ModuleKey;
  readonly name: string;
  readonly description: string | null;
  readonly displayOrder: number;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export interface OrganizationModule {
  readonly key: ModuleKey;
  readonly name: string;
  readonly description: string | null;
  readonly displayOrder: number;
  readonly enabled: boolean;
}

export interface OrganizationModules {
  readonly organizationId: string;
  readonly modules: readonly OrganizationModule[];
}