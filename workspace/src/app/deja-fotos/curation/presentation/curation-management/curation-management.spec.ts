import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';

import {
  CurationManagementComponent,
} from './curation-management';

describe('CurationManagementComponent', () => {
  let fixture: ComponentFixture<CurationManagementComponent>;
  let component: CurationManagementComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        CurationManagementComponent,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(
      CurationManagementComponent,
    );

    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create the curation page with zeroed indicators', () => {
    expect(component).toBeTruthy();

    const indicators = Array.from(
      (
        fixture.nativeElement as HTMLElement
      ).querySelectorAll('.summary-card strong'),
    ).map(element => element.textContent?.trim());

    expect(indicators).toEqual([
      '0',
      '0',
      '0',
      '0',
    ]);
  });

  it('should start on facial recognition with empty states', () => {
    const content =
      (
        fixture.nativeElement as HTMLElement
      ).textContent ?? '';

    expect(component.activeTab()).toBe('recognition');
    expect(content).toContain(
      'Nenhuma mídia aguardando revisão.',
    );
    expect(content).toContain(
      'Nenhum rosto detectado.',
    );
    expect(content).toContain(
      'Nenhuma mídia na fila de revisão.',
    );
  });

  it('should navigate between the curation tabs', () => {
    component.selectTab('people');
    fixture.detectChanges();

    expect(
      (
        fixture.nativeElement as HTMLElement
      ).textContent,
    ).toContain('Nenhuma pessoa cadastrada.');

    component.selectTab('avatars');
    fixture.detectChanges();

    expect(
      (
        fixture.nativeElement as HTMLElement
      ).textContent,
    ).toContain('Nenhum avatar cadastrado.');
  });
});