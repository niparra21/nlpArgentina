"""Small dependency-free client for the local Ollama HTTP API."""

from __future__ import annotations

import json
from typing import Any
from urllib import error, request


DEFAULT_OLLAMA_URL = "http://localhost:11434"


class OllamaError(RuntimeError):
    """Raised when the local Ollama API cannot complete a request."""


def installed_model_names(tags_response: dict[str, Any]) -> set[str]:
    """Extract installed model tags from an Ollama /api/tags response."""

    return {
        str(model.get("name", ""))
        for model in tags_response.get("models", [])
        if model.get("name")
    }


def find_model(
    tags_response: dict[str, Any],
    model_name: str,
) -> dict[str, Any] | None:
    """Return metadata for one exact local model tag."""

    return next(
        (
            model
            for model in tags_response.get("models", [])
            if model.get("name") == model_name
            or model.get("model") == model_name
        ),
        None,
    )


class OllamaClient:
    """Synchronous JSON client limited to the endpoints used by this project."""

    def __init__(
        self,
        base_url: str = DEFAULT_OLLAMA_URL,
        *,
        timeout: float = 300,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request_json(
        self,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call one Ollama JSON endpoint."""

        data = None
        method = "GET"
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            method = "POST"
            headers["Content-Type"] = "application/json; charset=utf-8"

        http_request = request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with request.urlopen(
                http_request,
                timeout=self.timeout,
            ) as response:
                parsed = json.load(response)
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise OllamaError(
                f"Ollama respondió HTTP {exc.code}: {detail}"
            ) from exc
        except error.URLError as exc:
            raise OllamaError(
                "No se pudo contactar a Ollama. Confirme que la aplicación "
                f"esté abierta y que la API responda en {self.base_url}."
            ) from exc
        except TimeoutError as exc:
            raise OllamaError(
                f"Ollama superó el tiempo de espera de {self.timeout} s."
            ) from exc

        if not isinstance(parsed, dict):
            raise OllamaError("Ollama devolvió una respuesta JSON inesperada.")
        return parsed

    def version(self) -> dict[str, Any]:
        return self.request_json("/api/version")

    def tags(self) -> dict[str, Any]:
        return self.request_json("/api/tags")

    def chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request_json("/api/chat", payload=payload)
