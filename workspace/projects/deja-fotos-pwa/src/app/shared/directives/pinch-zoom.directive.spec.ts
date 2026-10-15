import {
  Component,
  viewChild,
} from '@angular/core';

import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';

import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest';

import { PinchZoomDirective } from './pinch-zoom.directive';

@Component({
  standalone: true,
  imports: [PinchZoomDirective],
  template: `
    <img
      appPinchZoom
      src="data:,"
      alt="Foto de teste"
    />
  `,
})
class TestHostComponent {
  readonly zoom = viewChild.required(PinchZoomDirective);
}

describe('PinchZoomDirective', () => {
  let fixture: ComponentFixture<TestHostComponent>;
  let directive: PinchZoomDirective;
  let image: HTMLImageElement;

  function touch(
    x: number,
    y: number,
  ): Touch {
    return {
      clientX: x,
      clientY: y,
    } as Touch;
  }

  function touchEvent(
    type: string,
    points: Touch[],
  ): TouchEvent {
    const event = new Event(type, {
      bubbles: true,
      cancelable: true,
    });

    Object.defineProperty(event, 'touches', {
      value: points,
    });

    Object.defineProperty(event, 'changedTouches', {
      value: points,
    });

    return event as TouchEvent;
  }

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(
      TestHostComponent,
    );

    fixture.detectChanges();

    directive = fixture.componentInstance.zoom();

    image = fixture.nativeElement.querySelector('img');
  });

  it('should zoom using two fingers', () => {
    image.dispatchEvent(
      touchEvent('touchstart', [
        touch(100, 100),
        touch(200, 100),
      ]),
    );

    image.dispatchEvent(
      touchEvent('touchmove', [
        touch(50, 100),
        touch(250, 100),
      ]),
    );

    expect(image.style.transform).toContain('scale(2)');
  });

  it('should limit zoom to 4x', () => {
    image.dispatchEvent(
      touchEvent('touchstart', [
        touch(100, 100),
        touch(200, 100),
      ]),
    );

    image.dispatchEvent(
      touchEvent('touchmove', [
        touch(0, 100),
        touch(600, 100),
      ]),
    );

    expect(image.style.transform).toContain('scale(4)');
  });

  it('should allow dragging when zoomed', () => {
    image.dispatchEvent(
      touchEvent('touchstart', [
        touch(100, 100),
        touch(200, 100),
      ]),
    );

    image.dispatchEvent(
      touchEvent('touchmove', [
        touch(50, 100),
        touch(250, 100),
      ]),
    );

    image.dispatchEvent(
      touchEvent('touchend', []),
    );

    Object.defineProperty(image, 'clientWidth', {
      configurable: true,
      value: 300,
    });

    Object.defineProperty(image, 'clientHeight', {
      configurable: true,
      value: 300,
    });

    image.dispatchEvent(
      touchEvent('touchstart', [
        touch(100, 100),
      ]),
    );

    image.dispatchEvent(
      touchEvent('touchmove', [
        touch(130, 120),
      ]),
    );

    expect(image.style.transform).toContain(
      'translate3d(30px, 20px, 0)',
    );
  });

  it('should prevent gesture propagation while zooming', () => {
    const event = touchEvent('touchstart', [
      touch(100, 100),
      touch(200, 100),
    ]);

    const propagationSpy = vi.spyOn(
      event,
      'stopPropagation',
    );

    image.dispatchEvent(event);

    expect(propagationSpy).toHaveBeenCalled();
  });

  it('should restore original scale and position', () => {
    image.dispatchEvent(
      touchEvent('touchstart', [
        touch(100, 100),
        touch(200, 100),
      ]),
    );

    image.dispatchEvent(
      touchEvent('touchmove', [
        touch(50, 100),
        touch(250, 100),
      ]),
    );

    directive.reset();

    expect(image.style.transform).toBe(
      'translate3d(0px, 0px, 0) scale(1)',
    );
  });
});