/*
 * Deja Workspace Angular Integration
 *
 * Workspace Welcome Widget
 *
 * Primeiro Widget visual institucional da Deja Platform.
 */

import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';

import {
  WorkspaceWidgetInstance,
} from '../../../core/workspace-sdk/runtime/workspace-widget';

/**
 * Componente visual do Widget inicial da Deja Platform.
 */
@Component({
  selector: 'deja-workspace-welcome-widget',
  standalone: true,
  template: `
    <article class="workspace-welcome-widget">

      <header class="workspace-welcome-widget__header">

        <span class="workspace-welcome-widget__eyebrow">
          Deja Platform
        </span>

        <h2 class="workspace-welcome-widget__title">
          {{ widgetInstance.title ?? 'Bem-vindo à Deja Platform' }}
        </h2>

      </header>

      <p class="workspace-welcome-widget__message">
        {{ message }}
      </p>

      <footer class="workspace-welcome-widget__footer">
        Workspace institucional inicializado com sucesso.
      </footer>

    </article>
  `,
  styles: `
    :host {
      display: block;
      width: 100%;
      height: 100%;
    }

    .workspace-welcome-widget {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      box-sizing: border-box;
      width: 100%;
      min-height: 14rem;
      padding: 1.5rem;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 0.75rem;
      background:
        linear-gradient(
          145deg,
          rgba(255, 255, 255, 0.06),
          rgba(255, 255, 255, 0.02)
        );
    }

    .workspace-welcome-widget__header {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .workspace-welcome-widget__eyebrow {
      font-size: 0.75rem;
      font-weight: 600;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      opacity: 0.65;
    }

    .workspace-welcome-widget__title {
      margin: 0;
      font-size: 1.5rem;
      font-weight: 600;
    }

    .workspace-welcome-widget__message {
      margin: 0;
      line-height: 1.6;
      opacity: 0.82;
    }

    .workspace-welcome-widget__footer {
      margin-top: auto;
      font-size: 0.8rem;
      opacity: 0.55;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceWelcomeWidgetComponent {

  /**
   * Instância declarativa do Widget no Dashboard.
   */
  @Input({
    required: true,
  })
  widgetInstance!: WorkspaceWidgetInstance;

  /**
   * Mensagem configurada para esta instância.
   */
  protected get message(): string {

    const configuredMessage =
      this.widgetInstance.configuration?.['message'];

    if (typeof configuredMessage === 'string') {
      return configuredMessage;
    }

    return (
      'A infraestrutura inicial da Deja Platform '
      + 'está funcionando corretamente.'
    );

  }

}