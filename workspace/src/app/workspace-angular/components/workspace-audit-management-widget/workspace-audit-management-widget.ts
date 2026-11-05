import { HttpClient, HttpParams } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, Input, OnDestroy, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { AuthenticationService } from '../../../platform/authentication/application/authentication.service';
import { getModuleRole } from '../../../platform/module-management/application/module-access';
import { WorkspaceWidgetInstance } from '../../../core/workspace-sdk/runtime/workspace-widget';
import { WorkspaceWidgetContext } from '../../../core/workspace-sdk/runtime/workspace-widget-context';

type AuditCategory =
  | 'without_date'
  | 'without_time'
  | 'pending_faces'
  | 'conflicting_dates'
  | 'unverified_dates'
  | 'without_album';

interface AuditMedia {
  readonly id: string;
  readonly original_name: string;
  readonly original_date: string | null;
  readonly original_date_precision: string | null;
  readonly album_id: string | null;
  readonly file_size: number;
  readonly original_date_verified: boolean;
  readonly original_date_conflict: boolean;
  readonly was_converted: boolean;
}
interface AuditPage {
  readonly items: readonly AuditMedia[];
  readonly page: number;
  readonly total: number;
  readonly total_pages: number;
}
interface AuditAlbum { readonly id: string; readonly name: string; readonly environment_id: string; }
interface AuditEnvironment { readonly id: string; readonly name: string; }
interface BulkResult {
  readonly succeeded_count: number;
  readonly failed_count: number;
  readonly results: readonly {
    readonly media_id: string;
    readonly success: boolean;
    readonly error_message: string | null;
  }[];
}

const categories: readonly { id: AuditCategory; label: string }[] = [
  { id: 'without_date', label: 'Sem data' },
  { id: 'without_time', label: 'Sem horário' },
  { id: 'pending_faces', label: 'Faces pendentes' },
  { id: 'conflicting_dates', label: 'Datas conflitantes' },
  { id: 'unverified_dates', label: 'Datas não verificadas' },
  { id: 'without_album', label: 'Sem álbum' },
];

@Component({
  selector: 'deja-workspace-audit-management-widget',
  standalone: true,
  imports: [FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section class="audit">
      <header><h1>Auditoria</h1><p>Localize e corrija informações incompletas do acervo, sem remover as fotografias de seus álbuns.</p></header>
      @if (canSelectEnvironment && environments().length) {
        <label>Ambiente
          <select [ngModel]="environmentId()" (ngModelChange)="changeEnvironment($event)">
            @for (environment of environments(); track environment.id) {
              <option [value]="environment.id">{{ environment.name }}</option>
            }
          </select>
        </label>
      }
      @if (error()) { <p role="alert" class="error">{{ error() }} <button type="button" (click)="refresh()">Tentar novamente</button></p> }
      @if (notice()) { <p role="status">{{ notice() }}</p> }
      <nav class="filters" aria-label="Categorias de auditoria">
        @for (category of categories; track category.id) {
          <button type="button" [class.active]="selectedCategory() === category.id"
            (click)="chooseCategory(category.id)">
            {{ category.label }} <strong>{{ totals()[category.id] ?? '—' }}</strong>
          </button>
        }
      </nav>
      <div class="toolbar">
        <h2>{{ categoryLabel() }} — {{ total() }} foto(s)</h2>
        <button type="button" (click)="refresh()" [disabled]="loading() || busy()">Atualizar</button>
      </div>
      @if (canManage && media().length) {
        <section class="audit-actions" aria-label="Ações em lote">
          <div class="audit-actions__heading">
            <span class="audit-actions__icon" aria-hidden="true">▧</span>
            <div><h3>Ações em lote</h3><small>{{ selectedIds().size }} selecionada(s)</small></div>
          </div>
          <div class="audit-actions__buttons">
            <button type="button" [class.active-command]="editor() === 'date'"
              [disabled]="busy() || !selectedIds().size" (click)="toggleEditor('date')">Corrigir data</button>
            <button type="button" [class.active-command]="editor() === 'album'"
              [disabled]="busy() || !selectedIds().size" (click)="toggleEditor('album')">Mover para álbum</button>
            @if (selectedCategory() === 'pending_faces') {
              <button type="button" (click)="reopenCuration()" [disabled]="busy() || !selectedIds().size">Enviar à Curadoria</button>
            }
            @if (selectedCategory() === 'unverified_dates') {
              <button type="button" (click)="verifyDates()" [disabled]="busy() || !selectedIds().size">Confirmar datas existentes</button>
            }
            @if (selectedCategory() === 'conflicting_dates') {
              <button type="button" (click)="clearDateConflicts()" [disabled]="busy() || !selectedIds().size">Limpar conflito após conferir</button>
            }
            <button type="button" class="clear-command" (click)="clearSelection()"
              [disabled]="busy() || !selectedIds().size">Limpar seleção</button>
          </div>
          @if (editor() === 'date') {
            <div class="audit-actions__editor">
              <label for="audit-date">Nova data original</label>
              <input id="audit-date" type="date" [ngModel]="bulkDate()"
                (ngModelChange)="bulkDate.set($event)" [disabled]="busy()" />
              <button type="button" class="apply-button" (click)="applyDate()"
                [disabled]="busy() || !bulkDate() || !selectedIds().size">Aplicar data</button>
            </div>
          }
          @if (editor() === 'album') {
            <div class="audit-actions__editor">
              <label for="audit-album">Álbum de destino</label>
              <select id="audit-album" [ngModel]="bulkAlbum()"
                (ngModelChange)="bulkAlbum.set($event)" [disabled]="busy()">
                <option value="">Selecione uma opção</option>
                @for (album of albums(); track album.id) {
                  <option [value]="album.id">{{ album.name }}</option>
                }
              </select>
              <button type="button" class="apply-button" (click)="applyAlbum()"
                [disabled]="busy() || !bulkAlbum() || !selectedIds().size">Aplicar álbum</button>
            </div>
          }
        </section>
      }
      @if (loading()) { <p role="status">Carregando fotografias...</p> }
      @else if (!media().length) { <p>Nenhuma fotografia encontrada nesta categoria.</p> }
      @else {
        @if (canManage) {
          <div class="selection-bar">
            <label><input type="checkbox" [checked]="allVisibleSelected()" (change)="selectVisible()" /> Selecionar página atual</label>
            <span>{{ selectedIds().size }} mídia(s) selecionada(s)</span>
          </div>
        }
        <div class="photos">
          @for (item of media(); track item.id) {
            <article class="media-card" [class.media-card--selected]="selectedIds().has(item.id)"
              [class.media-card--conflict]="item.original_date_conflict">
              <div class="media-card__preview">
                @if (thumbnailUrls().get(item.id); as thumb) {
                  <img [src]="thumb" [alt]="item.original_name" loading="lazy" />
                } @else { <div class="placeholder">Carregando miniatura...</div> }
                @if (canManage) {
                  <label class="media-card__selection" [title]="selectedIds().has(item.id) ? 'Remover da seleção' : 'Selecionar mídia'">
                    <input type="checkbox" [checked]="selectedIds().has(item.id)"
                      (change)="toggle(item.id)" [attr.aria-label]="'Selecionar ' + item.original_name" />
                  </label>
                }
                <span class="media-card__type">Imagem</span>
              </div>
              <div class="media-card__content">
                <header class="media-card__header">
                  <h3 [title]="item.original_name">{{ item.original_name }}</h3>
                  <span class="status-badge status-badge--ready">Pronta</span>
                </header>
                <dl>
                  <div><dt>Data</dt><dd [class.missing]="!item.original_date">{{ formatDate(item) }}</dd></div>
                  <div><dt>Álbum</dt><dd [title]="albumName(item.album_id)">{{ albumName(item.album_id) }}</dd></div>
                  <div><dt>Arquivo</dt><dd>{{ formatFileSize(item.file_size) }}</dd></div>
                </dl>
                @if (item.original_date_verified || item.original_date_conflict || item.was_converted) {
                  <div class="badges">
                    @if (item.original_date_verified) { <span class="status-badge verified">Data confirmada</span> }
                    @if (item.original_date_conflict) { <span class="status-badge conflict">Conflito de data</span> }
                    @if (item.was_converted) { <span class="status-badge">Convertida</span> }
                  </div>
                }
                @if (canManage) {
                  <button type="button" class="media-card__delete" [disabled]="deletingId() !== null || busy()"
                    (click)="deleteMedia(item)" [attr.aria-label]="'Excluir ' + item.original_name">
                    {{ deletingId() === item.id ? 'Excluindo...' : 'Excluir mídia' }}
                  </button>
                }
              </div>
            </article>
          }
        </div>
        <footer class="pagination">
          <button type="button" (click)="loadPage(page() - 1)" [disabled]="page() <= 1 || loading()">Anterior</button>
          Página {{ page() }} de {{ totalPages() }}
          <button type="button" (click)="loadPage(page() + 1)" [disabled]="page() >= totalPages() || loading()">Próxima</button>
        </footer>
      }
    </section>
  `,
  styles: [`
    :host { display:block; min-width:0; }
    .audit { display:grid; gap:.9rem; padding:1rem; color:var(--workspace-color-text,inherit); }
    h1 { margin:0 0 .2rem; font-size:clamp(1.6rem,3vw,2rem); }
    header p { margin:0; font-size:.82rem; color:var(--workspace-color-text-secondary,#64748b); }
    .filters { display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:.65rem; }
    .filters button { text-align:left; display:flex; justify-content:space-between; gap:.75rem; }
    button,select,input { font:inherit; }
    button,select,input[type=date] { border:1px solid var(--workspace-color-border,#cbd5e1); border-radius:var(--workspace-radius-md,.5rem); padding:.55rem .7rem; background:var(--workspace-color-surface,#fff); color:inherit; }
    button { cursor:pointer; font-size:.74rem; font-weight:700; } button:disabled { opacity:.5; cursor:not-allowed; }
    .filters .active { outline:2px solid var(--workspace-color-primary,#2563eb); }
    .toolbar,.pagination { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:.8rem; }
    .toolbar h2 { font-size:1rem; margin:0; }
    .audit-actions { display:grid; grid-template-columns:auto minmax(0,1fr); gap:.8rem 1.25rem; align-items:center; padding:.8rem 1rem; background:var(--workspace-color-surface,#fff); border:1px solid var(--workspace-color-border,#cbd5e1); border-radius:var(--workspace-radius-lg,.7rem); }
    .audit-actions__heading { display:flex; align-items:center; gap:.75rem; }
    .audit-actions__heading h3 { font-size:1rem; margin:0; } .audit-actions__heading small { font-size:.68rem; color:var(--workspace-color-text-secondary,#64748b); }
    .audit-actions__icon { font-size:1.4rem; color:var(--workspace-color-primary,#2563eb); }
    .audit-actions__buttons { display:flex; flex-wrap:wrap; gap:.55rem; align-items:center; }
    .audit-actions__buttons button { min-height:2.35rem; }
    .audit-actions__buttons .active-command { color:var(--workspace-color-primary,#2563eb); border-color:var(--workspace-color-primary,#2563eb); }
    .audit-actions__buttons .clear-command { border-color:transparent; color:var(--workspace-color-text-secondary,#64748b); }
    .audit-actions__editor { grid-column:1/-1; display:grid; grid-template-columns:auto minmax(14rem,26rem) auto; gap:.65rem; align-items:center; padding-top:.75rem; border-top:1px solid var(--workspace-color-border,#cbd5e1); }
    .audit-actions__editor label { font-size:.7rem; font-weight:800; color:var(--workspace-color-text-secondary,#64748b); }
    .audit-actions__editor .apply-button { background:var(--workspace-color-primary,#2563eb); color:#fff; }
    .selection-bar { display:flex; flex-wrap:wrap; justify-content:space-between; gap:.6rem; font-size:.74rem; color:var(--workspace-color-text-secondary,#64748b); }
    .selection-bar label { display:flex; align-items:center; gap:.55rem; font-weight:700; color:var(--workspace-color-text,inherit); cursor:pointer; }
    .selection-bar input,.media-card__selection input { width:1.05rem; height:1.05rem; margin:0; accent-color:var(--workspace-color-primary,#2563eb); }
    .photos { display:grid; grid-template-columns:repeat(auto-fill,minmax(min(100%,13rem),1fr)); gap:.7rem; }
    .media-card { min-width:0; overflow:hidden; background:var(--workspace-color-surface,#fff); border:1px solid var(--workspace-color-border,#cbd5e1); border-radius:var(--workspace-radius-md,.5rem); }
    .media-card--selected { border-color:var(--workspace-color-primary,#2563eb); box-shadow:0 0 0 2px color-mix(in srgb,var(--workspace-color-primary,#2563eb) 18%,transparent); }
    .media-card--conflict { border-color:var(--workspace-color-danger,#dc2626); }
    .media-card__preview { position:relative; aspect-ratio:16/9; overflow:hidden; background:#e2e8f0; }
    .media-card__preview img,.placeholder { width:100%; height:100%; object-fit:contain; }
    .placeholder { display:grid; place-items:center; color:#475569; font-size:.7rem; }
    .media-card__selection { position:absolute; z-index:2; top:.45rem; left:.45rem; width:1.75rem; height:1.75rem; display:grid; place-items:center; border-radius:var(--workspace-radius-sm,.25rem); background:color-mix(in srgb,#fff 88%,transparent); cursor:pointer; }
    .media-card__type { position:absolute; top:.45rem; right:.45rem; padding:.25rem .5rem; color:white; background:#111c; border-radius:999px; font-size:.62rem; font-weight:800; }
    .media-card__content { display:grid; gap:.55rem; padding:.7rem; }
    .media-card__header { display:flex; justify-content:space-between; align-items:center; gap:.5rem; min-width:0; }
    .media-card h3 { min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:.78rem; margin:0; }
    .status-badge { flex:0 0 auto; padding:.2rem .4rem; font-size:.6rem; font-weight:800; border-radius:999px; background:#e2e8f0; }
    .status-badge--ready,.verified { background:#dcfce7; color:#166534; }
    .conflict { background:#fee2e2; color:#991b1b; }
    .media-card dl { display:grid; gap:.35rem; margin:0; }
    .media-card dl > div { display:flex; justify-content:flex-start; gap:.65rem; min-width:0; font-size:.68rem; }
    .media-card dt { flex:0 0 3.2rem; color:var(--workspace-color-text-secondary,#64748b); }
    .media-card dd { min-width:0; margin:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-weight:700; }
    .media-card dd.missing { color:#ef4444; }
    .badges { display:flex; flex-wrap:wrap; gap:.35rem; }
    .curation-link { border:0; padding:0; text-align:left; color:var(--workspace-color-primary,#2563eb); background:transparent; }
    .media-card__delete { display:block; width:100%; margin-top:.3rem; padding:0; border:0; color:var(--workspace-color-danger,#ef4444); background:transparent; font-size:.82rem; font-weight:700; text-align:center; }
    .error { color:#b91c1c; }
    @media (max-width:72rem) { .audit-actions { grid-template-columns:1fr; } }
    @media (max-width:40rem) { .audit-actions__editor { grid-template-columns:1fr; } }
  `],
})
export class WorkspaceAuditManagementWidgetComponent implements OnInit, OnDestroy {
  @Input({ required: true }) widgetInstance!: WorkspaceWidgetInstance;
  @Input({ required: true }) widgetContext!: WorkspaceWidgetContext;
  private readonly http = inject(HttpClient);
  private readonly user = inject(AuthenticationService).user();
  readonly canManage = this.user?.role === 'platform_admin' || getModuleRole(this.user, 'fotos') === 'manager';
  readonly canSelectEnvironment = this.user?.role === 'platform_admin';
  readonly categories = categories;
  readonly environments = signal<readonly AuditEnvironment[]>([]);
  readonly environmentId = signal(this.user?.environmentId ?? '');
  readonly totals = signal<Partial<Record<AuditCategory, number>>>({});
  readonly selectedCategory = signal<AuditCategory>('without_date');
  readonly media = signal<readonly AuditMedia[]>([]);
  readonly albums = signal<readonly AuditAlbum[]>([]);
  readonly thumbnailUrls = signal<ReadonlyMap<string,string>>(new Map());
  readonly selectedIds = signal<ReadonlySet<string>>(new Set());
  readonly bulkDate = signal('');
  readonly bulkAlbum = signal('');
  readonly editor = signal<'date' | 'album' | null>(null);
  readonly loading = signal(false);
  readonly busy = signal(false);
  readonly deletingId = signal<string | null>(null);
  readonly error = signal<string | null>(null);
  readonly notice = signal<string | null>(null);
  readonly page = signal(1);
  readonly total = signal(0);
  readonly totalPages = signal(0);
  private generation = 0;
  private destroyed = false;

  ngOnInit(): void { void this.initialize(); }
  ngOnDestroy(): void { this.destroyed = true; this.generation++; this.releaseThumbnails(); }
  categoryLabel(): string { return categories.find(c => c.id === this.selectedCategory())?.label ?? ''; }
  allVisibleSelected(): boolean {
    return this.media().length > 0 && this.media().every(item => this.selectedIds().has(item.id));
  }
  private async initialize(): Promise<void> {
    try {
      const environments = await firstValueFrom(this.http.get<readonly AuditEnvironment[]>('/api/v1/environments'));
      if (this.destroyed) return;
      this.environments.set(environments);
      if (!this.environmentId() && environments.length === 1) this.environmentId.set(environments[0].id);
    } catch { /* Escopo padrão do usuário continua utilizável. */ }
    await this.refresh();
  }
  changeEnvironment(id: string): void { this.environmentId.set(id); void this.refresh(); }
  chooseCategory(id: AuditCategory): void { this.selectedCategory.set(id); this.clearSelection(); void this.loadPage(1); }
  clearSelection(): void { this.selectedIds.set(new Set()); this.editor.set(null); }
  toggleEditor(value: 'date' | 'album'): void { this.editor.update(current => current === value ? null : value); }
  albumName(id: string | null): string { return id ? this.albums().find(a => a.id === id)?.name ?? 'Álbum não identificado' : 'Sem álbum'; }
  formatDate(media: AuditMedia): string {
    if (!media.original_date) return 'Sem data';
    const date = media.original_date.slice(0,10).split('-');
    const value = date.length === 3 ? date.reverse().join('/') : media.original_date.slice(0,10);
    return media.original_date_precision === 'datetime' || media.original_date.slice(11,16) === '12:00' ? value + ' ' + media.original_date.slice(11,16) : value;
  }
  formatFileSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }
  toggle(id: string): void {
    const next = new Set(this.selectedIds());
    if (next.has(id)) next.delete(id); else if (next.size < 100) next.add(id);
    this.selectedIds.set(next);
  }
  selectVisible(): void {
    const next = new Set(this.selectedIds());
    if (this.allVisibleSelected()) this.media().forEach(item => next.delete(item.id));
    else this.media().forEach(item => { if (next.size < 100) next.add(item.id); });
    this.selectedIds.set(next);
  }
  private params(): HttpParams {
    let p = new HttpParams();
    if (this.environmentId()) p = p.set('environment_id', this.environmentId());
    return p;
  }
  async refresh(): Promise<void> {
    this.clearSelection();
    const generation = ++this.generation;
    try {
      const [totals, albums] = await Promise.all([
        firstValueFrom(this.http.get<Record<AuditCategory,number>>('/api/fotos/media/audit/summary', { params:this.params() })),
        firstValueFrom(this.http.get<readonly AuditAlbum[]>('/api/fotos/albums', { params:this.params() })),
      ]);
      if (this.destroyed || generation !== this.generation) return;
      this.totals.set(totals);
      this.albums.set(albums.filter(a => !this.environmentId() || a.environment_id === this.environmentId()));
    } catch { if (generation === this.generation) this.error.set('Não foi possível atualizar os indicadores da auditoria.'); }
    if (generation === this.generation) await this.loadPage(1);
  }
  async loadPage(page: number): Promise<void> {
    const generation = ++this.generation;
    this.loading.set(true); this.error.set(null);
    this.clearSelection();
    try {
      const response = await firstValueFrom(this.http.get<AuditPage>('/api/fotos/media/audit/media', {
        params:this.params().set('category',this.selectedCategory()).set('page',String(page)).set('page_size','24'),
      }));
      if (this.destroyed || generation !== this.generation) return;
      this.releaseThumbnails();
      this.media.set(response.items);
      this.page.set(response.page); this.total.set(response.total); this.totalPages.set(response.total_pages);
      void this.loadThumbnails(response.items,generation);
    } catch {
      if (generation === this.generation) this.error.set('Não foi possível carregar as fotografias da categoria.');
    } finally {
      if (generation === this.generation) this.loading.set(false);
    }
  }
  private async loadThumbnails(items: readonly AuditMedia[],generation:number):Promise<void> {
    for (const item of items) {
      if (this.destroyed || generation !== this.generation) return;
      try {
        const blob = await firstValueFrom(this.http.get('/api/fotos/media/'+item.id+'/thumbnail',{responseType:'blob'}));
        if (this.destroyed || generation !== this.generation) return;
        const url=URL.createObjectURL(blob);
        this.thumbnailUrls.update(current=>new Map(current).set(item.id,url));
      } catch { /* Imagem faltante não interrompe a galeria. */ }
    }
  }
  private releaseThumbnails(): void {
    this.thumbnailUrls().forEach(url=>URL.revokeObjectURL(url));
    this.thumbnailUrls.set(new Map());
  }
  async reopenCuration(): Promise<void> {
    if (!this.canManage || !this.selectedIds().size || this.busy()) return;
    const count = this.selectedIds().size;
    await this.applyBulk({operation:'reopen_curation'});
    if (!this.error()) {
      this.notice.set(count + ' fotografia(s) encaminhada(s) à Curadoria, com os álbuns preservados.');
    }
  }
  async applyDate(): Promise<void> {
    if (!this.bulkDate() || !this.selectedIds().size || this.busy()) return;
    await this.applyBulk({operation:'set_original_date',original_date:this.bulkDate()+'T12:00:00',original_date_precision:'datetime'});
  }
  async deleteMedia(media: AuditMedia): Promise<void> {
    if (!this.canManage || this.deletingId() || this.busy()) return;
    if (!window.confirm(
      'Excluir permanentemente "' + media.original_name +
      '"? O arquivo e seus derivados serão removidos. Outras fotos e pessoas continuarão cadastradas.'
    )) return;
    this.deletingId.set(media.id);
    this.error.set(null);
    this.notice.set(null);
    try {
      await firstValueFrom(this.http.delete<void>('/api/fotos/media/' + media.id));
      const targetPage = this.media().length === 1 && this.page() > 1 ? this.page() - 1 : this.page();
      await this.refresh();
      if (targetPage > 1) await this.loadPage(targetPage);
      this.notice.set('Mídia excluída com sucesso.');
    } catch {
      this.error.set('Não foi possível excluir a mídia.');
    } finally {
      this.deletingId.set(null);
    }
  }
  async verifyDates(): Promise<void> {
    if (!this.selectedIds().size || this.busy()) return;
    if (!window.confirm('Você conferiu as datas de '+this.selectedIds().size+' fotografia(s)? Confirma que estão corretas?')) return;
    await this.applyBulk({operation:'verify_original_date'});
  }
  async clearDateConflicts(): Promise<void> {
    if (!this.selectedIds().size || this.busy()) return;
    if (!window.confirm('O conflito de data foi realmente resolvido para '+this.selectedIds().size+' fotografia(s)?')) return;
    await this.applyBulk({operation:'clear_original_date_conflict'});
  }
  async applyAlbum(): Promise<void> {
    if (!this.bulkAlbum() || !this.selectedIds().size || this.busy()) return;
    if (!window.confirm('Associar '+this.selectedIds().size+' fotografia(s) ao álbum selecionado?')) return;
    await this.applyBulk({operation:'set_album',album_id:this.bulkAlbum()});
  }
  private async applyBulk(action:
    | {operation:'set_original_date';original_date:string;original_date_precision:'date'|'datetime'}
    | {operation:'set_album';album_id:string}
    | {operation:'verify_original_date'}
    | {operation:'clear_original_date_conflict'}
    | {operation:'reopen_curation'}
  ):Promise<void> {
    this.busy.set(true); this.error.set(null); this.notice.set(null);
    try {
      const result=await firstValueFrom(this.http.patch<BulkResult>('/api/fotos/media/bulk',{
        ...action,media_ids:[...this.selectedIds()],
      }));
      const failed = result.results.filter(item => !item.success);
      await this.refresh();
      if (failed.length) {
        this.error.set(result.failed_count + ' mídia(s) não atualizada(s): ' +
          failed.slice(0, 3).map(item => item.error_message || 'Falha não identificada').join('; '));
      }
      if (result.succeeded_count) {
        this.notice.set(result.succeeded_count + ' mídia(s) atualizada(s) com sucesso.');
      }
    } catch { this.error.set('Não foi possível aplicar a operação em lote.'); }
    finally { this.busy.set(false); }
  }
}
