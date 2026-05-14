from __future__ import annotations

import httpx

from app.config import Settings


def _technical_detail(exc: Exception) -> str:
    detail = str(exc).strip()
    if detail:
        return detail
    return exc.__class__.__name__


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

    if "token invalido" in detail.lower() or "401" in detail or "403" in detail:
        return (
            f"[{label}] El gateway rechazó la autenticación (token inválido o sin permisos).\n"
            "Revisa OPENCLAW_*_GATEWAY_TOKEN en docker/telegram/.env.\n"
            f"Detalle: {detail}"
        )

    if "chat/completions" in detail.lower() or "404" in detail:
        return (
            f"[{label}] El gateway respondió, pero falta habilitar el endpoint "
            "/v1/chat/completions en su configuración.\n"
            f"Detalle: {detail}"
        )

    return (
        f"[{label}] Hubo un problema al {action}.\n"
        "El workspace sigue configurado; revisa /estado o intenta de nuevo.\n"
        f"Detalle: {detail}"
    )
