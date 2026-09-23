import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';

import {
  Media,
  MediaService,
} from '../../media';

import {
  Person,
} from '../domain/person';

import {
  PersonService,
} from '../application/person-service';

import {
  PersonPanelComponent,
} from './person-panel';

const person: Person = {
  id: 'person-1',
  organizationId: 'organization-1',
  tenantId: 'tenant-1',
  environmentId: 'environment-1',
  name: 'Ana',
  description: null,
  active: true,
  avatarContentType: null,
  createdAt: '2026-09-23T10:00:00',
  updatedAt: '2026-09-23T10:00:00',
};

function media(id: string): Media {
  return {
    id,
    originalName: `${id}.jpg`,
    mediaType: 'image',
    processingStatus: 'received',
    originalDate: null,
    originalDatePrecision: null,
  } as Media;
}

describe('PersonPanelComponent', () => {
  let fixture: ComponentFixture<PersonPanelComponent>;
  let component: PersonPanelComponent;
  let listByPerson: ReturnType<typeof vi.fn>;
  let listMedia: ReturnType<typeof vi.fn>;
  let createPerson: ReturnType<typeof vi.fn>;
  let linkMedia: ReturnType<typeof vi.fn>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PersonPanelComponent],
    }).compileComponents();

    listByPerson = vi.fn().mockResolvedValue({
      items: [],
      page: 1,
      pageSize: 24,
      total: 0,
      totalPages: 0,
    });
    listMedia = vi.fn().mockResolvedValue({
      items: [],
      page: 1,
      pageSize: 24,
      total: 0,
      totalPages: 0,
    });
    createPerson = vi.fn();
    linkMedia = vi.fn().mockResolvedValue(undefined);

    const personService = {
      create: createPerson,
      linkMedia,
      loadAvatar: vi.fn(),
    } as unknown as PersonService;

    const mediaService = {
      listByPerson,
      list: listMedia,
      loadThumbnail: vi.fn(),
    } as unknown as MediaService;

    fixture = TestBed.createComponent(
      PersonPanelComponent,
    );
    component = fixture.componentInstance;
    fixture.componentRef.setInput(
      'service',
      personService,
    );
    fixture.componentRef.setInput(
      'mediaService',
      mediaService,
    );
  });

  afterEach(() => {
    fixture.destroy();
  });

  it('loads person media by page without resetting the gallery', async () => {
    listByPerson
      .mockResolvedValueOnce({
        items: [media('media-1')],
        page: 1,
        pageSize: 24,
        total: 2,
        totalPages: 2,
      })
      .mockResolvedValueOnce({
        items: [media('media-2')],
        page: 2,
        pageSize: 24,
        total: 2,
        totalPages: 2,
      });

    fixture.componentRef.setInput('person', person);
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    expect(component.items().map(item => item.id))
      .toEqual(['media-1']);
    expect(listByPerson)
      .toHaveBeenCalledWith('person-1', 1, 24);

    await component.loadMore();
    fixture.detectChanges();
    await fixture.whenStable();

    expect(component.items().map(item => item.id))
      .toEqual(['media-1', 'media-2']);
    expect(listByPerson)
      .toHaveBeenCalledWith('person-1', 2, 24);
    expect(listByPerson)
      .toHaveBeenCalledTimes(2);
  });

  it('creates a person in the selected environment', async () => {
    createPerson.mockResolvedValue(person);
    const saved = vi.fn();
    component.saved.subscribe(saved);

    fixture.componentRef.setInput('creating', true);
    fixture.componentRef.setInput(
      'defaultEnvironmentId',
      'environment-1',
    );
    fixture.detectChanges();

    component.name.set('Ana');

    fixture.componentRef.setInput('canEdit', true);
    fixture.detectChanges();
    await component.save();

    expect(createPerson).toHaveBeenCalledWith({
      environmentId: 'environment-1',
      name: 'Ana',
      description: '',
      active: true,
    });
    expect(saved).toHaveBeenCalledWith(person);
  });

  it('only searches media within the selected person scope', async () => {
    fixture.componentRef.setInput('person', person);
    fixture.componentRef.setInput('canOrganize', true);
    fixture.detectChanges();
    await fixture.whenStable();

    component.openPicker();
    await fixture.whenStable();

    expect(listMedia).toHaveBeenCalledWith({
      organizationId: 'organization-1',
      tenantId: 'tenant-1',
      environmentId: 'environment-1',
      page: 1,
      pageSize: 24,
    });
  });
});