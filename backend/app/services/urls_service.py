from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.models.domain import UrlEncurtada, Usuario
from app.repositories.urls import UrlRepository
from app.schemas.urls import AcessoResponse, BatchDeleteRequest, UrlCreate, UrlResponse, UrlUpdate
from app.services.cache_service import CacheService


def url_to_response(url: UrlEncurtada) -> UrlResponse:
    return UrlResponse(
        codigo=url.codigo,
        url_original=url.url_original,
        usuario_id=url.usuario_id,
        criado_em=url.criado_em,
        atualizado_em=url.atualizado_em,
        desabilitado=url.desabilitado,
        data_expiracao=url.data_expiracao,
        qr_code=url.qr_code,
        url_encurtada=f"{get_settings().api_base_url}/u/{url.codigo}",
    )


def is_expired(expiration) -> bool:
    if not expiration:
        return False

    if expiration.tzinfo is None:
        expiration = expiration.replace(tzinfo=timezone.utc)
    return expiration < datetime.now(timezone.utc)


class UrlService:
    def __init__(self, urls: UrlRepository, cache: CacheService):
        self.urls = urls
        self.cache = cache

    def cadastrar(self, payload: UrlCreate, usuario: Usuario) -> UrlResponse:
        try:
            url = self.urls.create(usuario.id, str(payload.url_original), payload.alias, payload.expires_at())
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
        return url_to_response(url)

    def listar(self, usuario: Usuario, limit: int = 50) -> list[UrlResponse]:
        return [url_to_response(url) for url in self.urls.list_by_user(usuario.id, limit)]

    def buscar(self, codigo: str, usuario: Usuario) -> UrlResponse:
        url = self.urls.find_by_codigo(codigo)
        if not url or url.usuario_id != usuario.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL nao encontrada.")
        return url_to_response(url)

    def editar(self, codigo: str, payload: UrlUpdate, usuario: Usuario) -> UrlResponse:
        url = self.urls.update_redirect(
            codigo=codigo,
            usuario_id=usuario.id,
            url_original=str(payload.url_original),
            data_expiracao=payload.expires_at(),
            desabilitado=payload.desabilitado,
            manter_expiracao="ttl" not in payload.model_fields_set,
        )
        if not url:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL nao encontrada.")
        return url_to_response(url)

    def deletar(self, codigo: str, usuario: Usuario) -> None:
        if not self.urls.delete(codigo, usuario.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL nao encontrada.")

    def deletar_em_lote(self, payload: BatchDeleteRequest, usuario: Usuario) -> None:
        for codigo in payload.codigos:
            self.urls.delete(codigo, usuario.id)

    def acessar(self, codigo: str) -> str:
        cached_data = self.cache.get(codigo)
        if cached_data:
            return cached_data["url"]

        url = self.urls.find_by_codigo(codigo)
        if not url:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL nao encontrada.")

        if url.desabilitado:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="URL desabilitada.")

        if is_expired(url.data_expiracao):
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="URL expirada.")

        self.urls.register_access(codigo)
        self.urls.increment_access_counter(codigo)
        
        count = self.urls.get_access_count(codigo)
        if count == 50:
            settings = get_settings()
            self.cache.set(codigo, {"codigo": codigo, "url": url.url_original}, ttl_seconds=settings.redis_ttl_seconds)

        return url.url_original

    def listar_acessos(self, codigo: str, usuario: Usuario, limit: int = 100) -> list[AcessoResponse]:
        url = self.urls.find_by_codigo(codigo)
        if not url or url.usuario_id != usuario.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL nao encontrada.")

        return [
            AcessoResponse(codigo=acesso.codigo, dia=acesso.dia, id=acesso.id, acessado_em=acesso.acessado_em)
            for acesso in self.urls.list_accesses(codigo, limit=limit)
        ]
