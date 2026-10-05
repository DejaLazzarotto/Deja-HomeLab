import {
  ChangeDetectionStrategy,
  Component,
  inject,
} from '@angular/core';

import {
  Router,
} from '@angular/router';

@Component({
  selector: 'app-explore-page',
  standalone: true,
  templateUrl: './explore-page.html',
  styleUrl: './explore-page.scss',
  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class ExplorePageComponent {
  private readonly router =
    inject(Router);

  openDates(): void {
    void this.router.navigateByUrl(
      '/dates',
    );
  }
}