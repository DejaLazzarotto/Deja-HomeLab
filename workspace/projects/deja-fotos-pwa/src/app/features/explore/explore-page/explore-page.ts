import {
  ChangeDetectionStrategy,
  Component,
} from '@angular/core';

@Component({
  selector: 'app-explore-page',
  standalone: true,
  templateUrl: './explore-page.html',
  styleUrl: './explore-page.scss',
  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class ExplorePageComponent {}