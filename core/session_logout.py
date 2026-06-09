from django.contrib.auth import logout as auth_logout


def close_paldaca_session(request):
    """Cierra la sesion Django compartida (SSO) en la BD unificada."""
    auth_logout(request)
    if hasattr(request, "session"):
        request.session.flush()
