import {
  HttpClient,
} from '@angular/common/http';

import {
  ModuleManagementService,
} from './application';

import {
  HttpModuleManagementRepository,
} from './infrastructure';

export class ModuleManagementComposition {

  private readonly repository:
    HttpModuleManagementRepository;

  readonly service: ModuleManagementService;

  constructor(
    http: HttpClient,
  ) {
    this.repository =
      new HttpModuleManagementRepository(http);

    this.service =
      new ModuleManagementService(
        this.repository,
      );
  }

}