from functools import wraps
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from core.embed import embed_signal_response, is_embedded

from .constants import MODULO_CODIGO


def _usuario_tiene_acceso(request):
    user = request.user
    module_codes = getattr(request, "paldaca_module_codes", None)
    if module_codes is not None:
        return user.is_authenticated and MODULO_CODIGO in module_codes
    return (
        user.is_authenticated
        and hasattr(user, "tiene_acceso_modulo")
        and user.tiene_acceso_modulo(MODULO_CODIGO)
    )


def redirect_to_sso_login(request):
    """Manda al login del Portal conservando la URL actual en ?next=.

    Sin eso, tras autenticarse el usuario cae en el home del Portal y pierde
    el flujo (p. ej. /q/<token>/alta/ desde el móvil).
    """
    login_url = settings.PALDACA_SSO_LOGIN_URL
    next_url = request.build_absolute_uri()
    parts = urlsplit(login_url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["next"] = next_url
    return redirect(
        urlunsplit(
            (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
        )
    )


def _deny_unauthenticated(request):
    # Dentro del iframe un redirect al login del Portal anida el shell
    # (LoginPage hace frame-bust → deep link → otra vez iframe) y se percibe
    # como bucle al abrir fichas. El protocolo deja que el shell revalide.
    if is_embedded(request):
        return embed_signal_response(request, "session-expired")
    return redirect_to_sso_login(request)


def requiere_modulo_paldaca(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _deny_unauthenticated(request)
        if _usuario_tiene_acceso(request):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("No tienes acceso a este programa.")

    return _wrapped


class ModuloActivoRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if _usuario_tiene_acceso(request):
            return super().dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return _deny_unauthenticated(request)
        if is_embedded(request):
            return embed_signal_response(request, "forbidden")
        return HttpResponseForbidden("No tienes acceso a este programa.")
