/*
 * Deja Indicadores
 *
 * Companies Presentation
 *
 * Componente responsável pela apresentação e gerenciamento
 * da listagem de empresas.
 */

import {
  ChangeDetectionStrategy,
  Component,
  Input,
  OnInit,
  signal,
} from '@angular/core';

import {
  Company,
  CompanyService,
} from '../../index';

@Component({
  selector: 'deja-company-list',
  standalone: true,
  templateUrl: './company-list.html',
  styleUrl: './company-list.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CompanyListComponent implements OnInit {

  @Input({
    required: true,
  })
  service!: CompanyService;

  readonly companies = signal<readonly Company[]>([]);

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.companies.set(
      this.service.list(),
    );
  }

  trackCompany(
    index: number,
    company: Company,
  ): string {
    return company.id;
  }

}