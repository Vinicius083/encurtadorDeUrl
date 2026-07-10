from fastapi import Depends, Response, status
from fastapi.responses import RedirectResponse

from app.api.dependencies import get_current_user
from app.db.cassandra import get_session
from app.models.domain import Usuario
from app.repositories.urls import UrlRepository
from app.schemas.urls import AcessoResponse, BatchDeleteRequest, UrlCreate, UrlResponse, UrlUpdate
from app.services.cache_service import CacheService
from app.services.urls_service import UrlService


def get_url_repository() -> UrlRepository:
    return UrlRepository(get_session())


def get_cache_service() -> CacheService:
    return CacheService()


def get_url_service(
    urls: UrlRepository = Depends(get_url_repository),
    cache: CacheService = Depends(get_cache_service),
) -> UrlService:
    return UrlService(urls, cache)


def cadastrar_url(
    payload: UrlCreate,
    service: UrlService = Depends(get_url_service),
    usuario: Usuario = Depends(get_current_user),
) -> UrlResponse:
    return service.cadastrar(payload, usuario)


def listar_urls(
    limit: int = 50,
    service: UrlService = Depends(get_url_service),
    usuario: Usuario = Depends(get_current_user),
) -> list[UrlResponse]:
    return service.listar(usuario, limit)


def buscar_url(
    codigo: str,
    service: UrlService = Depends(get_url_service),
    usuario: Usuario = Depends(get_current_user),
) -> UrlResponse:
    return service.buscar(codigo, usuario)


def editar_url(
    codigo: str,
    payload: UrlUpdate,
    service: UrlService = Depends(get_url_service),
    usuario: Usuario = Depends(get_current_user),
) -> UrlResponse:
    return service.editar(codigo, payload, usuario)


def deletar_url(
    codigo: str,
    service: UrlService = Depends(get_url_service),
    usuario: Usuario = Depends(get_current_user),
) -> Response:
    service.deletar(codigo, usuario)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def deletar_urls_em_lote(
    payload: BatchDeleteRequest,
    service: UrlService = Depends(get_url_service),
    usuario: Usuario = Depends(get_current_user),
) -> Response:
    service.deletar_em_lote(payload, usuario)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def acessar_url(
    codigo: str,
    service: UrlService = Depends(get_url_service),
) -> RedirectResponse:
    url_original = service.acessar(codigo)
    return RedirectResponse(url_original, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


def listar_acessos(
    codigo: str,
    limit: int = 100,
    service: UrlService = Depends(get_url_service),
    usuario: Usuario = Depends(get_current_user),
) -> list[AcessoResponse]:
    return service.listar_acessos(codigo, usuario, limit)
