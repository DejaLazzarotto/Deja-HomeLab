import {
  Component,
  OnInit,
  inject,
} from '@angular/core';

import {
  WorkspaceBootstrapService,
} from './workspace-angular/bootstrap/workspace-bootstrap.service';

import {
  bootstrapWorkspace,
} from './workspace-angular/bootstrap/workspace-bootstrap';

import {
  createWorkspaceRuntimeContext,
} from './workspace-angular/bootstrap/workspace-runtime-context';

import {
  WorkspaceRootComponent,
} from './workspace-angular/components/workspace-root/workspace-root';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    WorkspaceRootComponent,
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {

  private readonly workspace =
    inject(WorkspaceBootstrapService);

  async ngOnInit(): Promise<void> {

    await bootstrapWorkspace(
      this.workspace,
      createWorkspaceRuntimeContext(),
    );

  }

}
