import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import Modulo, UsuarioModulo

UserModel = get_user_model()


@pytest.fixture
def usuario_activos_admin(db, client):
    user = UserModel.objects.create_user(
        username="admin-activos",
        email="admin-activos@test.com",
        password="test-pass-123",
        first_name="Admin",
        last_name="Activos",
    )
    modulo, _ = Modulo.objects.get_or_create(
        codigo="activos", defaults={"nombre": "Activos"}
    )
    UsuarioModulo.objects.get_or_create(usuario=user, modulo=modulo)
    client.force_login(user)
    return user


@pytest.mark.django_db
def test_usuarios_requiere_sesion(client):
    response = client.get(reverse("usuarios:usuario-search"))
    assert response.status_code == 302
    assert "login" in response.url.lower()


@pytest.mark.django_db
def test_busqueda_usuarios_core(usuario_activos_admin, client):
    UserModel.objects.create_user(
        username="V-99999",
        email="empleado@test.com",
        password="unused",
        first_name="Juan",
        last_name="Pérez",
        is_active=True,
    )
    response = client.get(reverse("usuarios:usuario-search"), {"buscar": "Juan"})
    assert response.status_code == 200
    assert b"Juan" in response.content


@pytest.mark.django_db
def test_crear_usuario_core(usuario_activos_admin, client):
    response = client.post(
        reverse("usuarios:usuario-create"),
        {
            "first_name": "María",
            "last_name": "Gómez",
            "email": "maria@test.com",
            "telefono": "04141234567",
            "perfil": "",
            "is_active": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    user = UserModel.objects.get(email="maria@test.com")
    assert user.first_name == "María"
    assert user.email == "maria@test.com"
