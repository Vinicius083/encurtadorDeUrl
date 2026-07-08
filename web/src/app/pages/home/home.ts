import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ToastService } from '../../shared/services/toast.service';
import { AuthService } from '../../shared/services/auth.service';
import { UrlService } from '../../shared/services/url.service';
import { formatErrorMessage } from '../../shared/utils/error-formatter';

export interface ShortUrl {
  id: string;
  alias: string;
  originalUrl: string;
  shortUrl: string;
  status: 'active' | 'expired';
  createdAt: string;
  ttl: string;
  qrCode?: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class HomeComponent implements OnInit {
  private readonly router = inject(Router);
  private readonly fb = inject(FormBuilder);
  private readonly toastService = inject(ToastService);
  private readonly authService = inject(AuthService);
  private readonly urlService = inject(UrlService);

  readonly userName = signal('Usuário');
  readonly urls = signal<ShortUrl[]>([]);
  readonly registerForm: FormGroup;
  readonly editForm: FormGroup;
  
  readonly selectedUrl = signal<ShortUrl | null>(null);
  readonly showQrModal = signal(false);
  readonly showEditModal = signal(false);
  readonly showDeleteModal = signal(false);
  
  readonly currentPage = signal(1);
  readonly itemsPerPage = 5;
  readonly totalPages = computed(() => Math.ceil(this.urls().length / this.itemsPerPage) || 1);
  
  readonly paginatedUrls = computed(() => {
    const startIndex = (this.currentPage() - 1) * this.itemsPerPage;
    return this.urls().slice(startIndex, startIndex + this.itemsPerPage);
  });

  constructor() {
    this.registerForm = this.fb.group({
      alias: [''],
      originalUrl: ['', [Validators.required, Validators.pattern(/https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/)]],
      expiration: ['7']
    });

    this.editForm = this.fb.group({
      id: [''],
      alias: [{ value: '', disabled: true }],
      originalUrl: ['', [Validators.required, Validators.pattern(/https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/)]],
      status: ['active']
    });
  }

  ngOnInit() {
    if (!this.authService.isAuthenticated()) {
      this.toastService.warning('Acesso Negado', 'Por favor, realize o login para acessar o painel.');
      this.router.navigate(['/']);
      return;
    }

    this.userName.set(this.authService.userName());
    this.loadUrls();
  }

  private loadUrls() {
    this.urlService.listar().subscribe({
      next: (data) => {
        this.urls.set(data);
      },
      error: (err) => {
        const errorMsg = formatErrorMessage(err);
        this.toastService.error('Erro ao Carregar', errorMsg);
      }
    });
  }

  onRegisterUrl() {
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      this.toastService.warning('Erro de Cadastro', 'Insira uma URL de origem válida.');
      return;
    }

    const { alias, originalUrl, expiration } = this.registerForm.value;
    const ttlDays = expiration === 'never' ? undefined : parseInt(expiration, 10);

    this.urlService.cadastrar(originalUrl.trim(), alias, ttlDays).subscribe({
      next: (newUrl) => {
        this.urls.update(current => [newUrl, ...current]);
        this.registerForm.reset({ expiration: '7' });
        this.toastService.success('URL Encurtada', `Link encurtado criado com sucesso!`);
      },
      error: (err) => {
        const errorMsg = formatErrorMessage(err);
        this.toastService.error('Erro de Cadastro', errorMsg);
      }
    });
  }

  openEditModal(url: ShortUrl) {
    this.selectedUrl.set(url);
    this.editForm.patchValue({
      id: url.id,
      alias: url.alias,
      originalUrl: url.originalUrl,
      status: url.status
    });
    this.showEditModal.set(true);
  }

  onSaveEdit() {
    if (this.editForm.invalid) {
      this.toastService.warning('Formulário Inválido', 'Corrija os campos do formulário antes de salvar.');
      return;
    }

    const { id, originalUrl, status } = this.editForm.getRawValue();
    const desabilitado = status === 'expired';

    this.urlService.editar(id, originalUrl.trim(), desabilitado).subscribe({
      next: (updatedUrl) => {
        this.urls.update(current => current.map(u => u.id === id ? updatedUrl : u));
        this.showEditModal.set(false);
        this.selectedUrl.set(null);
        this.toastService.success('Link Atualizado', 'As alterações do link foram salvas com sucesso.');
      },
      error: (err) => {
        const errorMsg = formatErrorMessage(err);
        this.toastService.error('Erro de Atualização', errorMsg);
      }
    });
  }

  openDeleteModal(url: ShortUrl) {
    this.selectedUrl.set(url);
    this.showDeleteModal.set(true);
  }

  confirmDelete() {
    const urlToDelete = this.selectedUrl();
    if (!urlToDelete) return;

    this.urlService.deletar(urlToDelete.id).subscribe({
      next: () => {
        this.urls.update(current => current.filter(u => u.id !== urlToDelete.id));
        
        if (this.currentPage() > this.totalPages()) {
          this.currentPage.set(this.totalPages());
        }

        this.showDeleteModal.set(false);
        this.selectedUrl.set(null);
        this.toastService.success('Link Excluído', 'O link encurtado foi removido permanentemente.');
      },
      error: (err) => {
        const errorMsg = formatErrorMessage(err);
        this.toastService.error('Erro de Exclusão', errorMsg);
      }
    });
  }

  openQrModal(url: ShortUrl) {
    this.selectedUrl.set(url);
    this.showQrModal.set(true);
  }

  closeAllModals() {
    this.showQrModal.set(false);
    this.showEditModal.set(false);
    this.showDeleteModal.set(false);
    this.selectedUrl.set(null);
  }

  copyToClipboard(text: string) {
    navigator.clipboard.writeText(text).then(() => {
      this.toastService.success('Copiado', 'Link copiado para a área de transferência.');
    }).catch(() => {
      this.toastService.error('Erro de Cópia', 'Não foi possível copiar o link.');
    });
  }

  nextPage() {
    if (this.currentPage() < this.totalPages()) {
      this.currentPage.update(p => p + 1);
    }
  }

  prevPage() {
    if (this.currentPage() > 1) {
      this.currentPage.update(p => p - 1);
    }
  }

  logout() {
    this.authService.clearSession();
    this.toastService.info('Logout Realizado', 'Você saiu da sua conta.');
    this.router.navigate(['/']);
  }
}
