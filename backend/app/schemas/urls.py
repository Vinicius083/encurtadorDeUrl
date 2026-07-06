from datetime import date, datetime, timedelta, timezone

from pydantic import BaseModel, Field, HttpUrl, field_validator


class UrlCreate(BaseModel):
    url_original: HttpUrl
    alias: str | None = Field(default=None, min_length=3, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    ttl: int | None = Field(default=7, ge=1, le=365, description="Tempo em dias.")

    def expires_at(self) -> datetime | None:
        if self.ttl is None:
            return None
        return datetime.now(timezone.utc) + timedelta(days=self.ttl)


class UrlUpdate(BaseModel):
    url_original: HttpUrl
    ttl: int | None = Field(default=None, ge=1, le=365)
    desabilitado: bool | None = None

    def expires_at(self) -> datetime | None:
        if self.ttl is None:
            return None
        return datetime.now(timezone.utc) + timedelta(days=self.ttl)


class UrlResponse(BaseModel):
    codigo: str
    url_original: str
    usuario_id: int
    criado_em: datetime
    atualizado_em: datetime
    desabilitado: bool
    data_expiracao: datetime | None
    qr_code: str | None
    url_encurtada: str


class BatchDeleteRequest(BaseModel):
    codigos: list[str] = Field(min_length=1, max_length=100)

    @field_validator("codigos")
    @classmethod
    def validate_codigos(cls, value: list[str]) -> list[str]:
        return list(dict.fromkeys(value))


class AcessoResponse(BaseModel):
    codigo: str
    dia: date
    id: int
    acessado_em: datetime
