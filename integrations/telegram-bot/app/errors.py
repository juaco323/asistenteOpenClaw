from __future__ import annotations

import re

import httpx

from app.config import Settings

_STATUS_CODE_RE = re.compile(r"'(\d{3})[ ']|HTTP (\d{3})")


def _technical_detail(exc: Exception) -> str:
    detail = str(exc).strip()
    if detail:
        return detail
    return exc.__class__.__name__


def _status_code(detail: str) -> int | None:
    match = _STATUS_CODE_RE.search(detail)
    if not match:
        return None
    return int(match.group(1) or match.group(2))


def _is_timeout(exc: Exception) -> bool:
    if isinstance(exc, (TimeoutError, httpx.TimeoutException)):
        return True
    lowered = str(exc).lower()
    return "timeout" in lowered or "timed out" in lowered


def _is_connection(exc: Exception) -> bool:
    if isinstance(exc, (httpx.ConnectError, httpx.NetworkError, ConnectionError, OSError)):
        return True
    lowered = str(exc).lower()
    return any(
        token in lowered
        for token in (
            "connection refused",
            "connect error",
            "network",
            "name or service not known",
            "failed to connect",
        )
    )


def format_gateway_error(
    settings: Settings,
    workspace_name: str,
    exc: Exception,
    *,
    action: str = "procesar tu mensaje",
) -> str:
    workspace = settings.get_workspace(workspace_name)
    label = workspace.label
    detail = _technical_detail(exc)

    if _is_timeout(exc):
        return (
            f"[{label}] Recibí tu solicitud, pero {action} tardó más de lo esperado.\n"
            "El gateway puede seguir trabajando en segundo plano; no significa que OpenClaw "
            "esté caído.\n"
            "Prueba en unos segundos con una pregunta corta (por ejemplo: «¿en qué estado "
            "quedó la tarea anterior?») o divide la petición en pasos más pequeños.\n"
            f"Detalle: {detail}"
        )

    if _is_connection(exc):
        return (
            f"[{label}] No pude conectar con el gateway en {workspace.base_url}.\n"
            "Verifica que el servicio esté activo con /estado y que el contenedor o servicio "
            f"de {label.lower()} esté levantado.\n"
            f"Detalle: {detail}"
        )

    status = _status_code(detail)

    if status in (401, 403) or "token invalido" in detail.lower():
        return (
            f"[{label}] El gateway rechazó la autenticación (token inválido o sin permisos).\n"
            "Revisa OPENCLAW_*_GATEWAY_TOKEN en docker/telegram/.env.\n"
            f"Detalle: {detail}"
        )

    if status == 404:
        return (
            f"[{label}] El gateway respondió, pero falta habilitar el endpoint "
            "/v1/chat/completions en su configuración.\n"
            f"Detalle: {detail}"
        )

    if status is not None and status >= 500:
        lowered = detail.lower()
        if any(token in lowered for token in ("quota", "billing", "rate_limit", "rate limit")):
            return (
                f"[{label}] El proveedor del modelo (OpenAI) rechazó la petición por cuota/facturación "
                f"(HTTP {status}) al {action}.\n"
                "No es un problema de `gog` ni de Gmail: revisa el plan y el saldo de la cuenta en "
                "https://platform.openai.com/account/billing y la variable OPENAI_API_KEY.\n"
                f"Detalle: {detail}"
            )
        return (
            f"[{label}] El gateway respondió con un error interno (HTTP {status}) al {action}.\n"
            "El endpoint sí está habilitado: el fallo suele venir de una herramienta que invocó el "
            "agente (p. ej. OAuth de Gmail/Calendar vencido o revocado en `gog`, o un comando fallido) "
            "o del proveedor del modelo — revisa el detalle abajo antes de asumir la causa.\n"
            "Si menciona `gog`/OAuth: `gog auth list` en el contenedor y, si expiró, "
            "./scripts/gog-auth-setup.sh en el host.\n"
            f"Detalle: {detail}"
        )

    return (
        f"[{label}] Hubo un problema al {action}.\n"
        "El workspace sigue configurado; revisa /estado o intenta de nuevo.\n"
        f"Detalle: {detail}"
    )
