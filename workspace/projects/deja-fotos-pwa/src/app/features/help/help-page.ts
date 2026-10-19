import {
  ChangeDetectionStrategy,
  Component,
  inject,
} from '@angular/core';

import { Router } from '@angular/router';

interface HelpTopic {
  readonly id: string;
  readonly title: string;
  readonly description: string;
  readonly icon: string;
}

@Component({
  selector: 'app-help-page',
  standalone: true,
  templateUrl: './help-page.html',
  styleUrl: './help-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HelpPageComponent {
  private readonly router = inject(Router);

  readonly topics: readonly HelpTopic[] = [
    {
      id: 'dates',
      title: 'Por Datas',
      description: 'Encontre fotos pelo ano, mês e período.',
      icon: 'calendar',
    },
    {
      id: 'people',
      title: 'Por Pessoas e IA',
      description: 'Descubra como a inteligência artificial ajuda a organizar fotos.',
      icon: 'people',
    },
    {
      id: 'albums',
      title: 'Álbuns',
      description: 'Explore coleções de momentos especiais.',
      icon: 'albums',
    },
    {
      id: 'quick-access',
      title: 'Explorar rápido',
      description: 'Conheça Favoritos, Recentes e Vídeos.',
      icon: 'quick',
    },
    {
      id: 'viewer',
      title: 'Visualizar fotos e vídeos',
      description: 'Aprenda a abrir, deslizar, ampliar e voltar.',
      icon: 'viewer',
    },
  ];

  openTopic(topic: HelpTopic): void {
    void this.router.navigate(['/help', topic.id]);
  }

  goBack(): void {
    void this.router.navigateByUrl('/explore');
  }
}