import { HttpClient, HttpParams } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, Input, OnDestroy, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
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
interface BulkResult { readonly succeeded_count: number; readonly failed_count: number; }

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
                @if (selectedCategory() === 'pending_faces') {
                  <button type="button" class="curation-link" (click)="openCuration(item.id)">Corrigir face na Curadoria</button>
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
    .audit { padding:1rem; color:var(--workspace-color-text-primary,inherit); }
    h1 { margin:0 0 .4rem; } header p { margin:0 0 1rem; color:var(--workspace-color-text-secondary,#64748b); }
    .filters { display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:.65rem; margin:1rem 0; }
    .filters button { text-align:left; display:flex; justify-content:space-between; gap:.75rem; }
    button,select,input { font:inherit; }
    button,select,input[type=date] { border:1px solid var(--workspace-color-border,#cbd5e1); border-radius:.5rem; padding:.6rem; background:var(--workspace-color-surface,#fff); color:inherit; }
    button { cursor:pointer; } button:disabled { opacity:.5; cursor:not-allowed; }
    .active { outline:2px solid var(--workspace-color-primary,#2563eb); }
    .toolbar,.pagination { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:.8rem; margin:1rem 0; }
    .toolbar h2 { font-size:1.05rem; margin:0; }
    .bulk { display:flex; flex-wrap:wrap; align-items:end; gap:.75rem; padding:1rem; background:var(--workspace-color-surface,#f8fafc); border:1px solid var(--workspace-color-border,#cbd5e1); border-radius:.7rem; }
    .bulk label { display:flex; gap:.35rem; flex-direction:column; }
    .photos { display:grid; grid-template-columns:repeat(auto-fill,minmax(175px,1fr)); gap:1rem; }
    article { border:1px solid var(--workspace-color-border,#cbd5e1); border-radius:.7rem; padding:.65rem; min-width:0; }
    article img,.placeholder { width:100%; aspect-ratio:4/3; object-fit:cover; border-radius:.4rem; background:#e2e8f0; }
    .placeholder { display:grid; place-items:center; color:#475569; }
    article h3 { font-size:.85rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    article p { font-size:.8rem; color:var(--workspace-color-text-secondary,#64748b); }
    .choose { display:flex; gap:.35rem; align-items:center; margin-bottom:.4rem; }
    .error { color:#b91c1c; }
  `],
})
export class WorkspaceAuditManagementWidgetComponent implements OnInit, OnDestroy {
  @Input({ required: true }) widgetInstance!: WorkspaceWidgetInstance;
  @Input({ required: true }) widgetContext!: WorkspaceWidgetContext;
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
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
    return media.original_date_precision === 'datetime' ? value + ' ' + media.original_date.slice(11,16) : value;
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
  async openCuration(mediaId: string): Promise<void> {
    await this.router.navigate(['/fotos/curadoria'], { queryParams: { media_id: mediaId } });
  }
  async applyDate(): Promise<void> {
    if (!this.bulkDate() || !this.selectedIds().size || this.busy()) return;
    if (!window.confirm('Corrigir a data de '+this.selectedIds().size+' fotografia(s)? O sistema armazenará 12:00 como horário técnico.')) return;
    await this.applyBulk({operation:'set_original_date',original_date:this.bulkDate()+'T12:00:00',original_date_precision:'date'});
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
  ):Promise<void> {
    this.busy.set(true); this.error.set(null); this.notice.set(null);
    try {
      const result=await firstValueFrom(this.http.patch<BulkResult>('/api/fotos/media/bulk',{
        ...action,media_ids:[...this.selectedIds()],
      }));
      await this.refresh();
      this.notice.set(result.succeeded_count+' atualizada(s); '+result.failed_count+' falha(s).');
    } catch { this.error.set('Não foi possível aplicar a operação em lote.'); }
    finally { this.busy.set(false); }
  }
}
