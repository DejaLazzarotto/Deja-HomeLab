import {
  Component,
  OnInit,
  inject,
  signal,
} from '@angular/core';

import {
  RouterOutlet,
} from '@angular/router';

import {
  WorkspaceBootstrapService,
} from './workspace-angular/bootstrap/workspace-bootstrap.service';

import {
  bootstrapWorkspace,
} from './workspace-angular/bootstrap/workspace-bootstrap';

import {
  createWorkspaceRuntimeContext,
} from './workspace-angular/bootstrap/workspace-runtime-context';

@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {

  protected readonly title = signal('deja-workspace');

  private readonly workspace =
    inject(WorkspaceBootstrapService);

  async ngOnInit(): Promise<void> {

    await bootstrapWorkspace(
      this.workspace,
      createWorkspaceRuntimeContext(),
    );

  }

}
