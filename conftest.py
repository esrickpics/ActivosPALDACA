import pytest
from django.contrib.auth import get_user_model

from activos.models import Categoria, SubCategoria, Ubicacion
from core.models import Modulo, UsuarioModulo
from usuarios.models import UsuarioAsignado


@pytest.fixture
def user(db):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="pytest_user",
        email="pytest@example.com",
        password="test-pass-123",
    )
    modulo, _ = Modulo.objects.get_or_create(codigo="activos", defaults={"nombre": "Activos"})
    UsuarioModulo.objects.get_or_create(usuario=user, modulo=modulo)
    return user


@pytest.fixture
def client_auth(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def catalogo(db):
    """Categoría, subcategoría, dos ubicaciones y dos usuarios asignables."""
    cat = Categoria.objects.create(nombre="Categoría Pytest")
    sub = SubCategoria.objects.create(nombre="Sub Pytest", categoria=cat)
    u_almacen = Ubicacion.objects.create(nombre="Ubicación Almacén Pytest")
    u_oficina = Ubicacion.objects.create(nombre="Ubicación Oficina Pytest")
    ua = UsuarioAsignado.objects.create(
        nombres="Ana",
        apellidos="Prueba",
        identificacion="V-PYTEST-001",
    )
    ub = UsuarioAsignado.objects.create(
        nombres="Luis",
        apellidos="Prueba",
        identificacion="V-PYTEST-002",
    )
    return {
        "categoria": cat,
        "subcategoria": sub,
        "ubicacion_almacen": u_almacen,
        "ubicacion_oficina": u_oficina,
        "usuario_a": ua,
        "usuario_b": ub,
    }
