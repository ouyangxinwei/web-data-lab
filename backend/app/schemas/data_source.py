"""Validation schemas for data-source API requests and responses."""
import re
from datetime import datetime
from typing import Any, Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator


_SECRET_KEY_PARTS = (
    "password",
    "secret",
    "token",
    "credential",
    "authorization",
    "apikey",
    "accesskey",
    "privatekey",
)


def _validate_http_url(value: str) -> str:
    """Accept absolute HTTP(S) URLs without embedded credentials.

    This validates stored configuration only. Any future collector that makes
    outbound requests must additionally enforce SSRF protections at request time.
    """
    value = value.strip()
    try:
        parsed = urlsplit(value)
        # Accessing .port also validates malformed port values.
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("base_url must be a valid absolute HTTP(S) URL") from exc

    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValueError("base_url must use http:// or https:// and include a hostname")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("base_url must not contain a username or password")
    if parsed.fragment:
        raise ValueError("base_url must not contain a URL fragment")
    return value


def _reject_secret_fields(value: Any, path: str = "config_json") -> None:
    """Prevent credentials from being accidentally persisted in source config."""
    if isinstance(value, dict):
        for key, nested_value in value.items():
            normalized_key = re.sub(r"[^a-z0-9]", "", str(key).lower())
            if any(part in normalized_key for part in _SECRET_KEY_PARTS):
                raise ValueError(
                    f"{path}.{key} looks like a credential field; store secrets outside data-source config"
                )
            _reject_secret_fields(nested_value, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested_value in enumerate(value):
            _reject_secret_fields(nested_value, f"{path}[{index}]")


class DataSourceBase(BaseModel):
    """Fields shared by data-source creation and replacement."""

    name: str = Field(min_length=1, max_length=150)
    source_type: Literal["api", "html"]
    base_url: str = Field(min_length=1)
    description: str | None = None
    config_json: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError("name must not be empty")
        return value

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, value: str) -> str:
        return _validate_http_url(value)

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None

    @field_validator("config_json")
    @classmethod
    def validate_config_json(cls, value: dict[str, Any]) -> dict[str, Any]:
        _reject_secret_fields(value)
        return value


class DataSourceCreate(DataSourceBase):
    """Payload accepted when creating a data source."""


class DataSourceReplace(DataSourceBase):
    """Full replacement payload accepted by PUT /api/sources/{source_id}."""


class DataSourceRead(BaseModel):
    """Public representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    source_type: Literal["api", "html"]
    base_url: str
    description: str | None
    config_json: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DataSourceList(BaseModel):
    """Paginated data-source list response."""

    items: list[DataSourceRead]
    total: int
    limit: int
    offset: int
