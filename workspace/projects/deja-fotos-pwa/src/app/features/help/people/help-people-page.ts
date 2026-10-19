import {
  ChangeDetectionStrategy,
  Component,
  inject,
} from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-help-people-page',
  standalone: true,
  templateUrl: './help-people-page.html',
  styleUrl: './help-people-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HelpPeoplePageComponent {
  private readonly router = inject(Router);

  backToHelp(): void {
    void this.router.navigateByUrl('/help');
  }
}