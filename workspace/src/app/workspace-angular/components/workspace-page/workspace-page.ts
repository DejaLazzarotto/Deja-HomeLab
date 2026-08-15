import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
} from '@angular/core';

import {
  WorkspaceBootstrapService,
} from '../../bootstrap/workspace-bootstrap.service';

import {
  bootstrapWorkspace,
} from '../../bootstrap/workspace-bootstrap';

import {
  createWorkspaceRuntimeContext,
} from '../../bootstrap/workspace-runtime-context';

import {
  WorkspaceRootComponent,
} from '../workspace-root/workspace-root';

@Component({
  selector: 'deja-workspace-page',
  standalone: true,
  imports: [
    WorkspaceRootComponent,
  ],
  template: '<deja-workspace-root />',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspacePageComponent implements OnInit {

  private readonly workspace =
    inject(WorkspaceBootstrapService);

  async ngOnInit(): Promise<void> {
    await bootstrapWorkspace(
      this.workspace,
      createWorkspaceRuntimeContext(),
    );
  }

}