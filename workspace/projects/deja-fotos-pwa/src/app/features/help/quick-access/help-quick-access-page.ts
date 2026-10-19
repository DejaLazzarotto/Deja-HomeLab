import {
  ChangeDetectionStrategy,
  Component,
  inject,
} from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-help-quick-access-page',
  standalone: true,
  templateUrl: './help-quick-access-page.html',
  styleUrl: './help-quick-access-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HelpQuickAccessPageComponent {
  private readonly router = inject(Router);

  backToHelp(): void {
    void this.router.navigateByUrl('/help');
  }
}