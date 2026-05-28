from functools import wraps

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

MODULO_CODIGO = "activos"


def _usuario_tiene_acceso(user):
    return (
        user.is_authenticated
        and hasattr(user, "tiene_acceso_modulo")
        and user.tiene_acceso_modulo(MODULO_CODIGO)
    )


def requiere_modulo_paldaca(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if _usuario_tiene_acceso(request.user):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("No tienes acceso a este programa.")

    return _wrapped


class ModuloActivoRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if _usuario_tiene_acceso(request.user):
            return super().dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return redirect(settings.PALDACA_SSO_LOGIN_URL)
        return HttpResponseForbidden("No tienes acceso a este programa.")
