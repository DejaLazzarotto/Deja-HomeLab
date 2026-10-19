import {
  ChangeDetectionStrategy,
  Component,
  inject,
  signal,
} from '@angular/core';

import {
  Router,
} from '@angular/router';


import { WelcomeService } from '../../core/welcome/welcome.service';

@Component({
  selector: 'app-welcome-page',
  standalone: true,
  templateUrl: './welcome-page.html',
  styleUrl: './welcome-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WelcomePageComponent {
  private readonly router = inject(Router);

  private readonly welcomeService = inject(WelcomeService);


  readonly selectedInstallation = signal<'ios' | 'android' | null>(null);

  selectInstallation(platform: 'ios' | 'android'): void {
    this.selectedInstallation.update(
      current => current === platform ? null : platform,
    );
  }
  readonly currentPage = signal(0);

  readonly totalPages = 5;

  private touchStartX: number | null = null;
  private touchStartY: number | null = null;

  get isFirstPage(): boolean {
    return this.currentPage() === 0;
  }

  get isLastPage(): boolean {
    return this.currentPage() === this.totalPages - 1;
  }

  nextPage(): void {
    if (this.isLastPage) {
      return;
    }

    this.currentPage.update(
      page => Math.min(page + 1, this.totalPages - 1),
    );
  }

  previousPage(): void {
    this.currentPage.update(
      page => Math.max(page - 1, 0),
    );
  }

  goToPage(page: number): void {
    if (
      !Number.isInteger(page)
      || page < 0
      || page >= this.totalPages
    ) {
      return;
    }

    this.currentPage.set(page);
  }

  onTouchStart(event: TouchEvent): void {
    const touch = event.changedTouches[0];

    if (!touch) {
      return;
    }

    this.touchStartX = touch.clientX;
    this.touchStartY = touch.clientY;
  }

  onTouchEnd(event: TouchEvent): void {
    const touch = event.changedTouches[0];

    if (
      !touch
      || this.touchStartX === null
      || this.touchStartY === null
    ) {
      return;
    }

    const deltaX = touch.clientX - this.touchStartX;
    const deltaY = touch.clientY - this.touchStartY;

    this.touchStartX = null;
    this.touchStartY = null;

    if (
      Math.abs(deltaX) < 60
      || Math.abs(deltaX) <= Math.abs(deltaY)
    ) {
      return;
    }

    if (deltaX < 0) {
      this.nextPage();
    } else {
      this.previousPage();
    }
  }

  skip(): void {
    this.welcomeService.markCompleted();
    void this.router.navigateByUrl('/login');
  }
}
