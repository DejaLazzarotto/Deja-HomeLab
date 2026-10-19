import {
  ChangeDetectionStrategy,
  Component,
  inject,
} from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-help-dates-page',
  standalone: true,
  templateUrl: './help-dates-page.html',
  styleUrl: './help-dates-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HelpDatesPageComponent {
  private readonly router = inject(Router);

  backToHelp(): void {
    void this.router.navigateByUrl('/help');
  }
}