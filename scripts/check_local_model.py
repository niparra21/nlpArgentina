"""Run a small, reproducible smoke test against a local Ollama model.

This script does not execute the complete RAG pipeline. It verifies the layer
that will generate answers later: Ollama availability, model installation,
grounded answering, citations, abstention and basic latency metrics.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ollama_client import (
    DEFAULT_OLLAMA_URL,
    OllamaClient,
    OllamaError,
    installed_model_names,
)

DEFAULT_MODEL = "qwen3.5:9b"
SYSTEM_PROMPT = (
    "Usa exclusivamente el contexto proporcionado. Puedes hacer conclusiones "
    "directas que estén inequívocamente respaldadas por el contexto, pero "
    "nunca añadas conocimiento externo. Responde brevemente y termina cada "
    "afirmación respaldada con su identificador, por ejemplo [F1]. Si el "
    "contexto no contiene información suficiente, responde exactamente: "
    "No encontrado en el contexto."
)
CONTEXT = (
    "Contexto [F1]: El Laboratorio Aurora abre de lunes a viernes de "
    "8:00 a 16:00. No abre los fines de semana."
)


@dataclass(frozen=True)
class SmokeCase:
    """One controlled question and its deterministic validation rules."""

    name: str
    question: str
    expected_substrings: tuple[str, ...] = ()
    expected_exact: str | None = None


SMOKE_CASES = (
    SmokeCase(
        name="respuesta_con_evidencia",
        question=(
            "¿En qué horario abre el Laboratorio Aurora de lunes a viernes?"
        ),
        expected_substrings=("8:00", "16:00", "[F1]"),
    ),
    SmokeCase(
        name="abstencion_sin_evidencia",
        question="¿Cuál es el número de teléfono del Laboratorio Aurora?",
        expected_exact="No encontrado en el contexto.",
    ),
)


def answer_is_valid(case: SmokeCase, answer: str) -> bool:
    """Validate one answer without requiring identical generative wording."""

    normalized = answer.strip()
    if case.expected_exact is not None:
        return normalized == case.expected_exact
    return all(fragment in normalized for fragment in case.expected_substrings)


def chat_payload(
    model: str,
    case: SmokeCase,
    *,
    num_ctx: int,
    keep_alive: str,
) -> dict[str, Any]:
    """Build the deterministic chat request used by the smoke test."""

    return {
        "model": model,
        "stream": False,
        "think": False,
        "keep_alive": keep_alive,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"{CONTEXT}\n\nPregunta: {case.question}",
            },
        ],
        "options": {
            "num_ctx": num_ctx,
            "temperature": 0.1,
            "seed": 42,
            "num_predict": 128,
        },
    }


def result_summary(
    case: SmokeCase,
    response: dict[str, Any],
) -> dict[str, Any]:
    """Select human-readable answer and timing fields from Ollama output."""

    answer = str(response.get("message", {}).get("content", "")).strip()
    eval_count = int(response.get("eval_count", 0))
    eval_duration = int(response.get("eval_duration", 0))
    tokens_per_second = (
        eval_count / (eval_duration / 1_000_000_000)
        if eval_count and eval_duration
        else 0.0
    )
    return {
        "case": case.name,
        "passed": answer_is_valid(case, answer),
        "answer": answer,
        "total_seconds": round(
            int(response.get("total_duration", 0)) / 1_000_000_000,
            2,
        ),
        "load_seconds": round(
            int(response.get("load_duration", 0)) / 1_000_000_000,
            2,
        ),
        "prompt_tokens": int(response.get("prompt_eval_count", 0)),
        "output_tokens": eval_count,
        "tokens_per_second": round(tokens_per_second, 2),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Comprueba Ollama y un modelo generativo local.",
    )
    parser.add_argument("--api-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--num-ctx", type=int, default=8192)
    parser.add_argument("--keep-alive", default="5m")
    parser.add_argument("--timeout", type=float, default=300)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.num_ctx <= 0:
        print("ERROR: --num-ctx debe ser positivo.", file=sys.stderr)
        return 2

    try:
        client = OllamaClient(args.api_url, timeout=args.timeout)
        version = client.version()
        tags = client.tags()
        if args.model not in installed_model_names(tags):
            print(
                f"ERROR: el modelo {args.model!r} no está instalado. "
                f"Ejecute: ollama pull {args.model}",
                file=sys.stderr,
            )
            return 2

        print(
            json.dumps(
                {
                    "ollama_version": version.get("version"),
                    "model": args.model,
                    "num_ctx": args.num_ctx,
                    "thinking": False,
                },
                ensure_ascii=False,
                indent=2,
            )
        )

        results = []
        for case in SMOKE_CASES:
            response = client.chat(
                chat_payload(
                    args.model,
                    case,
                    num_ctx=args.num_ctx,
                    keep_alive=args.keep_alive,
                )
            )
            summary = result_summary(case, response)
            results.append(summary)
            print(json.dumps(summary, ensure_ascii=False, indent=2))

        passed = sum(result["passed"] for result in results)
        print(f"Resultado: {passed}/{len(results)} pruebas superadas.")
        return 0 if passed == len(results) else 1
    except OllamaError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
