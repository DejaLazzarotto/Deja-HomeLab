import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';

import {
  Album,
} from '../../../albums';

import {
  MediaBulkActionsComponent,
} from './media-bulk-actions';

function createAlbum(): Album {
  return {
    id: 'album-destination',
    organizationId: 'organization-1',
    tenantId: 'tenant-1',
    environmentId: 'environment-1',
    name: 'Destination album',
    description: null,
    active: true,
    createdAt: '2026-09-01T10:00:00.000Z',
    updatedAt: '2026-09-01T10:00:00.000Z',
  };
}

describe('MediaBulkActionsComponent', () => {
  let fixture: ComponentFixture<MediaBulkActionsComponent>;
  let component: MediaBulkActionsComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MediaBulkActionsComponent,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(
      MediaBulkActionsComponent,
    );

    component = fixture.componentInstance;
  });

  it('shows only album organization commands in organization mode', () => {
    fixture.componentRef.setInput(
      'mode',
      'album_organization',
    );
    fixture.componentRef.setInput(
      'selectedCount',
      1,
    );
    fixture.componentRef.setInput(
      'albums',
      [createAlbum()],
    );

    fixture.detectChanges();

    const content =
      (
        fixture.nativeElement as HTMLElement
      ).textContent ?? '';

    expect(component).toBeTruthy();
    expect(content).toContain('Organizar m\u00eddias');
    expect(content).toContain('Mover para \u00e1lbum');
    expect(content).toContain('Limpar sele\u00e7\u00e3o');
    expect(content).not.toContain('Corrigir data');
    expect(content).not.toContain('Confirmar datas');
    expect(content).not.toContain('Limpar conflitos');
  });
});
