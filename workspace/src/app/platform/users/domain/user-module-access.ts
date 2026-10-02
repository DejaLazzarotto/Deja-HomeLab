import {
  UserModuleRole,
} from '../../authentication/domain/authenticated-user';

import {
  ModuleKey,
} from '../../module-management/domain/module-key';

export interface UserModuleAccess {
  readonly key: ModuleKey;
  readonly name: string;
  readonly description: string | null;
  readonly displayOrder: number;
  readonly organizationEnabled: boolean;
  readonly hasAccess: boolean;
  readonly role: UserModuleRole | null;
}

export interface UserModuleAccessSelection {
  readonly moduleKey: ModuleKey;
  readonly role: UserModuleRole;
}

export interface UserModuleAccesses {
  readonly userId: string;
  readonly modules: readonly UserModuleAccess[];
}