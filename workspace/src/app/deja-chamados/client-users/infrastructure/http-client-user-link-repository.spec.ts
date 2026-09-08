import {
  HttpClient,
  provideHttpClient,
} from '@angular/common/http';

import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';

import {
  TestBed,
} from '@angular/core/testing';

import {
  HttpClientUserLinkRepository,
} from './http-client-user-link-repository';

describe('HttpClientUserLinkRepository', () => {

  let repository: HttpClientUserLinkRepository;

  let httpTesting:
    HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    repository =
      new HttpClientUserLinkRepository(
        TestBed.inject(HttpClient),
      );

    httpTesting =
      TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it(
    'deve consultar o vínculo pelo usuário',
    async () => {
      const promise =
        repository.findByUserId(
          'user-1',
        );

      const request =
        httpTesting.expectOne(
          '/api/chamados/client-users/user-1',
        );

      expect(request.request.method)
        .toBe('GET');

      request.flush({
        id: 'link-1',
        user_id: 'user-1',
        client_id: 'client-1',
        created_at: '2026-09-08T12:00:00',
      });

      await expect(promise)
        .resolves
        .toEqual({
          id: 'link-1',
          userId: 'user-1',
          clientId: 'client-1',
          createdAt: '2026-09-08T12:00:00',
        });
    },
  );

  it(
    'deve retornar undefined quando o vínculo não existir',
    async () => {
      const promise =
        repository.findByUserId(
          'user-sem-vinculo',
        );

      const request =
        httpTesting.expectOne(
          '/api/chamados/client-users/user-sem-vinculo',
        );

      request.flush(
        {
          detail: 'Vínculo não encontrado.',
        },
        {
          status: 404,
          statusText: 'Not Found',
        },
      );

      await expect(promise)
        .resolves
        .toBeUndefined();
    },
  );

  it(
    'deve criar um vínculo',
    async () => {
      const promise =
        repository.create({
          userId: 'user-1',
          clientId: 'client-1',
        });

      const request =
        httpTesting.expectOne(
          '/api/chamados/client-users',
        );

      expect(request.request.method)
        .toBe('POST');

      expect(request.request.body)
        .toEqual({
          user_id: 'user-1',
          client_id: 'client-1',
        });

      request.flush({
        id: 'link-1',
        user_id: 'user-1',
        client_id: 'client-1',
        created_at: '2026-09-08T12:00:00',
      });

      await expect(promise)
        .resolves
        .toEqual({
          id: 'link-1',
          userId: 'user-1',
          clientId: 'client-1',
          createdAt: '2026-09-08T12:00:00',
        });
    },
  );

  it(
    'deve atualizar o Cliente vinculado',
    async () => {
      const promise =
        repository.update(
          'user-1',
          {
            clientId: 'client-2',
          },
        );

      const request =
        httpTesting.expectOne(
          '/api/chamados/client-users/user-1',
        );

      expect(request.request.method)
        .toBe('PUT');

      expect(request.request.body)
        .toEqual({
          client_id: 'client-2',
        });

      request.flush({
        id: 'link-1',
        user_id: 'user-1',
        client_id: 'client-2',
        created_at: '2026-09-08T12:00:00',
      });

      await expect(promise)
        .resolves
        .toEqual({
          id: 'link-1',
          userId: 'user-1',
          clientId: 'client-2',
          createdAt: '2026-09-08T12:00:00',
        });
    },
  );

  it(
    'deve remover o vínculo',
    async () => {
      const promise =
        repository.delete(
          'user-1',
        );

      const request =
        httpTesting.expectOne(
          '/api/chamados/client-users/user-1',
        );

      expect(request.request.method)
        .toBe('DELETE');

      request.flush(null);

      await expect(promise)
        .resolves
        .toBeUndefined();
    },
  );

});