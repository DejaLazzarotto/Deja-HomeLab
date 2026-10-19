import {
  ChangeDetectionStrategy,
  Component,
  inject,
} from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-help-albums-page',
  standalone: true,
  templateUrl: './help-albums-page.html',
  styleUrl: './help-albums-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HelpAlbumsPageComponent {
  private readonly router = inject(Router);

  backToHelp(): void {
    void this.router.navigateByUrl('/help');
  }
}