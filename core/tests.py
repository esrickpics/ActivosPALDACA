from django.test import TestCase

from core.models import Modulo, UsuarioModulo, UsuarioPaldaca


class AccesoModuloTests(TestCase):
    def setUp(self):
        self.modulo_a, _ = Modulo.objects.get_or_create(
            codigo="activos", defaults={"nombre": "Activos"}
        )
        self.modulo_b, _ = Modulo.objects.get_or_create(
            codigo="calidad", defaults={"nombre": "Calidad"}
        )

        self.admin = UsuarioPaldaca.objects.create_user(
            username="admin@test.com",
            email="admin@test.com",
            password="testpass123",
            rol=UsuarioPaldaca.ROL_ADMINISTRADOR,
        )
        self.usuario = UsuarioPaldaca.objects.create_user(
            username="user@test.com",
            email="user@test.com",
            password="testpass123",
            rol=UsuarioPaldaca.ROL_USUARIO,
        )
        self.superadmin = UsuarioPaldaca.objects.create_superuser(
            username="root@test.com",
            email="root@test.com",
            password="testpass123",
        )

        UsuarioModulo.objects.create(usuario=self.admin, modulo=self.modulo_a)
        UsuarioModulo.objects.create(usuario=self.usuario, modulo=self.modulo_a)

    def test_administrador_solo_modulos_asignados(self):
        self.assertTrue(self.admin.tiene_acceso_modulo("activos"))
        self.assertFalse(self.admin.tiene_acceso_modulo("calidad"))
        self.assertEqual(
            [m.codigo for m in self.admin.modulos_habilitados()],
            ["activos"],
        )

    def test_administrador_en_modulo_vs_usuario(self):
        self.assertTrue(self.admin.es_administrador_en_modulo("activos"))
        self.assertFalse(self.usuario.es_administrador_en_modulo("activos"))
        self.assertTrue(self.usuario.tiene_acceso_modulo("activos"))

    def test_superuser_todos_los_modulos(self):
        self.assertTrue(self.superadmin.tiene_acceso_modulo("activos"))
        self.assertTrue(self.superadmin.tiene_acceso_modulo("calidad"))
        self.assertGreaterEqual(self.superadmin.modulos_habilitados().count(), 2)
        self.assertTrue(self.superadmin.es_administrador_en_modulo("calidad"))
        self.assertFalse(
            self.superadmin.accesos_modulo.exists(),
            "Superuser no requiere filas en core_usuario_modulo",
        )
