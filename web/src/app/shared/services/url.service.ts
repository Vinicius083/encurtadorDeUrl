import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { ShortUrl } from '../../pages/home/home';

export interface BackendUrlResponse {
  codigo: string;
  url_original: string;
  usuario_id: number;
  criado_em: string;
  atualizado_em: string;
  desabilitado: boolean;
  data_expiracao: string | null;
  qr_code: string | null;
  url_encurtada: string;
}

@Injectable({
  providedIn: 'root'
})
export class UrlService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://localhost:8000';

  private mapToShortUrl(res: BackendUrlResponse): ShortUrl {
    const isExpired = res.data_expiracao ? new Date(res.data_expiracao).getTime() < Date.now() : false;
    const status: 'active' | 'expired' = (res.desabilitado || isExpired) ? 'expired' : 'active';
    
    // Format Created Date (criado_em is ISO e.g. 2026-07-08T00:00:00Z)
    let createdAt = '';
    try {
      const createdDate = new Date(res.criado_em);
      createdAt = `${String(createdDate.getDate()).padStart(2, '0')}/${String(createdDate.getMonth() + 1).padStart(2, '0')}/${createdDate.getFullYear()}`;
    } catch {
      createdAt = '--/--/----';
    }

    // Format TTL
    let ttl = 'Permanente';
    if (res.data_expiracao) {
      if (isExpired) {
        ttl = 'Expirado';
      } else {
        const diffTime = new Date(res.data_expiracao).getTime() - Date.now();
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        if (diffDays <= 0) {
          ttl = 'Expirado';
        } else {
          ttl = diffDays === 1 ? '1 dia restante' : `${diffDays} dias restantes`;
        }
      }
    }

    return {
      id: res.codigo,
      alias: res.codigo,
      originalUrl: res.url_original,
      shortUrl: res.url_encurtada,
      status,
      createdAt,
      ttl,
      qrCode: res.qr_code || undefined
    };
  }

  listar(limit = 50): Observable<ShortUrl[]> {
    return this.http.get<BackendUrlResponse[]>(`${this.baseUrl}/url?limit=${limit}`).pipe(
      map(urls => urls.map(url => this.mapToShortUrl(url)))
    );
  }

  cadastrar(originalUrl: string, alias?: string, ttlDays?: number): Observable<ShortUrl> {
    const payload: { url_original: string; alias?: string; ttl?: number } = {
      url_original: originalUrl
    };
    if (alias && alias.trim()) {
      payload.alias = alias.trim();
    }
    if (ttlDays && ttlDays > 0) {
      payload.ttl = ttlDays;
    }

    return this.http.post<BackendUrlResponse>(`${this.baseUrl}/url`, payload).pipe(
      map(res => this.mapToShortUrl(res))
    );
  }

  editar(codigo: string, originalUrl: string, desabilitado: boolean, ttlDays?: number): Observable<ShortUrl> {
    const payload: { url_original: string; desabilitado: boolean; ttl?: number } = {
      url_original: originalUrl,
      desabilitado
    };
    if (ttlDays && ttlDays > 0) {
      payload.ttl = ttlDays;
    }

    return this.http.put<BackendUrlResponse>(`${this.baseUrl}/url/${codigo}`, payload).pipe(
      map(res => this.mapToShortUrl(res))
    );
  }

  deletar(codigo: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/url/${codigo}`);
  }
}
