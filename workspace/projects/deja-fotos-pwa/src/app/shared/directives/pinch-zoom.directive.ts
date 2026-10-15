import {
  Directive,
  ElementRef,
  HostListener,
  inject,
  input,
} from '@angular/core';

@Directive({
  selector: 'img[appPinchZoom]',
  standalone: true,
  host: {
    '[style.touch-action]': '"none"',
  },
})
export class PinchZoomDirective {
  private readonly element = inject(
    ElementRef<HTMLImageElement>,
  );

  readonly maxScale = input(4);

  private scale = 1;
  private translateX = 0;
  private translateY = 0;

  private initialDistance = 0;
  private initialScale = 1;

  private lastTouchX = 0;
  private lastTouchY = 0;

  private gestureWasPinch = false;
  private panActive = false;

  @HostListener('touchstart', ['$event'])
  onTouchStart(event: TouchEvent): void {
    if (event.touches.length >= 2) {
      this.gestureWasPinch = true;
      this.panActive = false;
      this.initialDistance = this.getDistance(event);
      this.initialScale = this.scale;

      event.stopPropagation();
      return;
    }

    if (event.touches.length === 1 && this.scale > 1) {
      const touch = event.touches[0];

      this.lastTouchX = touch.clientX;
      this.lastTouchY = touch.clientY;
      this.panActive = true;

      event.stopPropagation();
    }
  }

  @HostListener('touchmove', ['$event'])
  onTouchMove(event: TouchEvent): void {
    if (event.touches.length >= 2) {
      event.preventDefault();
      event.stopPropagation();

      if (!this.gestureWasPinch) {
        this.gestureWasPinch = true;
        this.initialDistance = this.getDistance(event);
        this.initialScale = this.scale;
        return;
      }

      if (this.initialDistance <= 0) {
        return;
      }

      const distance = this.getDistance(event);

      this.scale = Math.min(
        Math.max(
          this.initialScale *
            (distance / this.initialDistance),
          1,
        ),
        Math.max(1, this.maxScale()),
      );

      this.constrainTranslation();
      this.applyTransform();
      return;
    }

    if (event.touches.length !== 1) {
      return;
    }

    if (this.gestureWasPinch || this.scale > 1) {
      event.stopPropagation();
    }

    if (this.scale <= 1) {
      return;
    }

    event.preventDefault();

    const touch = event.touches[0];

    if (!this.panActive) {
      this.lastTouchX = touch.clientX;
      this.lastTouchY = touch.clientY;
      this.panActive = true;
      return;
    }

    this.translateX += touch.clientX - this.lastTouchX;
    this.translateY += touch.clientY - this.lastTouchY;

    this.lastTouchX = touch.clientX;
    this.lastTouchY = touch.clientY;

    this.constrainTranslation();
    this.applyTransform();
  }

  @HostListener('touchend', ['$event'])
  onTouchEnd(event: TouchEvent): void {
    const blockNavigation =
      this.gestureWasPinch || this.scale > 1;

    if (blockNavigation) {
      event.stopPropagation();
    }

    if (event.touches.length >= 2) {
      this.initialDistance = this.getDistance(event);
      this.initialScale = this.scale;
      this.panActive = false;
      return;
    }

    if (event.touches.length === 1) {
      const touch = event.touches[0];

      this.lastTouchX = touch.clientX;
      this.lastTouchY = touch.clientY;
      this.panActive = this.scale > 1;
      return;
    }

    this.panActive = false;
    this.gestureWasPinch = false;

    if (this.scale <= 1) {
      this.reset();
    }
  }

  @HostListener('touchcancel', ['$event'])
  onTouchCancel(event: TouchEvent): void {
    if (this.gestureWasPinch || this.scale > 1) {
      event.stopPropagation();
    }

    this.panActive = false;
    this.gestureWasPinch = false;

    if (this.scale <= 1) {
      this.reset();
    }
  }

  reset(): void {
    this.scale = 1;
    this.translateX = 0;
    this.translateY = 0;
    this.initialDistance = 0;
    this.initialScale = 1;
    this.gestureWasPinch = false;
    this.panActive = false;

    this.applyTransform();
  }

  private getDistance(event: TouchEvent): number {
    const first = event.touches[0];
    const second = event.touches[1];

    return Math.hypot(
      second.clientX - first.clientX,
      second.clientY - first.clientY,
    );
  }

  private constrainTranslation(): void {
    const image = this.element.nativeElement;

    const maxX = Math.max(
      0,
      (image.clientWidth * (this.scale - 1)) / 2,
    );

    const maxY = Math.max(
      0,
      (image.clientHeight * (this.scale - 1)) / 2,
    );

    this.translateX = Math.max(
      -maxX,
      Math.min(this.translateX, maxX),
    );

    this.translateY = Math.max(
      -maxY,
      Math.min(this.translateY, maxY),
    );
  }

  private applyTransform(): void {
    const image = this.element.nativeElement;

    image.style.transform =
      `translate3d(${this.translateX}px, ${this.translateY}px, 0) scale(${this.scale})`;
  }
}