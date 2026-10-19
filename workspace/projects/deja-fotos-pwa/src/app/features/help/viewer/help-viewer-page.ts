import {
  ChangeDetectionStrategy,
  Component,
  inject,
} from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-help-viewer-page',
  standalone: true,
  templateUrl: './help-viewer-page.html',
  styleUrl: './help-viewer-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HelpViewerPageComponent {
  private readonly router = inject(Router);

  backToHelp(): void {
    void this.router.navigateByUrl('/help');
  }
}