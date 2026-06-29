from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseBase


def _expire_cookie(
    response: HttpResponseBase,
    name: str,
    *,
    path: str,
    domain: str | None,
    secure: bool,
    httponly: bool,
    samesite: str,
) -> None:
    response.set_cookie(
        name,
        "",
        max_age=0,
        path=path,
        domain=domain,
        secure=secure,
        httponly=httponly,
        samesite=samesite,
    )


def apply_paldaca_cookie_clearance(response: HttpResponseBase) -> HttpResponseBase:
    """Fuerza borrado de cookies SSO en el dominio compartido (.cpaldaca.com)."""
    path = getattr(settings, "SESSION_COOKIE_PATH", "/") or "/"
    secure = getattr(settings, "SESSION_COOKIE_SECURE", False)
    samesite = getattr(settings, "SESSION_COOKIE_SAMESITE", "Lax")
    domain = getattr(settings, "SESSION_COOKIE_DOMAIN", None)
    csrf_domain = getattr(settings, "CSRF_COOKIE_DOMAIN", None) or domain

    cookie_specs = (
        (getattr(settings, "SESSION_COOKIE_NAME", "paldaca_sessionid"), True),
        ("sessionid", True),
        (getattr(settings, "CSRF_COOKIE_NAME", "csrftoken"), False),
    )

    domains: list[str | None] = [None]
    if domain:
        domains.append(domain)
    if csrf_domain and csrf_domain not in domains:
        domains.append(csrf_domain)

    for name, httponly in cookie_specs:
        for cookie_domain in domains:
            _expire_cookie(
                response,
                name,
                path=path,
                domain=cookie_domain,
                secure=secure,
                httponly=httponly,
                samesite=samesite,
            )

    return response


def close_paldaca_session(request):
    """Cierra la sesion Django compartida (SSO) en la BD unificada."""
    auth_logout(request)
    if hasattr(request, "session"):
        request.session.flush()
