# Guia: integrar programas satelite con Portal Paldaca (login unico)

Documento para implementar en **cada app Django** (HDT, Calidad, Codigos, Activos, etc.) el mismo modelo de identidad, sesion compartida y control de acceso por modulo.

**Portal Paldaca** = login principal (`http://localhost:5173/login` en dev).  
**Apps satelite** = solo validan sesion y permisos; no duplican usuarios.

---

## Respuesta corta: debo copiar `core`?

**Si.** Cada programa satelite debe incluir la app Django `core` de este repositorio (misma version de modelos y migraciones).

| Copiar | No copiar |
|--------|-----------|
| Carpeta `backend/core/` completa | App `portal/` (solo del portal) |
| Mismas migraciones `core/migrations/` | `views_auth.py` del portal si no usas API JWT en el satelite |
| `PaldacaSessionMiddleware` | Frontend React del portal |

### Formas de compartir `core`

1. **Copia manual (recomendado al inicio)**  
   Copia `Portal-Paldaca/backend/core/` al proyecto satelite (ej. `core_HDT/core/` o reemplaza la app local si existia).  
   Cuando cambie el modelo en el portal, vuelves a sincronizar la carpeta.

2. **Submodulo Git (futuro)**  
   Repo `paldaca-core` publicado y cada satelite lo referencia como submodulo.

3. **Paquete pip privado (futuro)**  
   Solo si el equipo crece; no es necesario ahora.

**Regla:** todos los programas deben usar la **misma version** de migraciones `core` contra la **misma base de datos**.

---

## Arquitectura objetivo

```
Usuario → Login en Portal (5173 / API 8000)
              ↓
         Cookie paldaca_sessionid + tabla django_session
              ↓
    ┌─────────┴─────────┬─────────────┐
    ↼                   ▼             ▼
 localhost:8001    :8002         :8003
 (HDT)            (Calidad)      (Activos)
    │                   │             │
    └─────────┬─────────┴─────────────┘
              ▼
        MySQL paldaca_db
   core_usuario, core_modulo, core_usuario_modulo, ...
```

### Reglas de negocio (implementadas en `core.models`)

| Quien | Acceso a modulos | Rol dentro del modulo |
|-------|------------------|------------------------|
| **Superuser** | Todos los activos | Administrador en todos |
| **`rol=administrador`** | Solo filas en `core_usuario_modulo` | Administrador en esos modulos |
| **`rol=usuario`** | Solo filas en `core_usuario_modulo` | Usuario normal |

Metodos clave en `request.user`:

- `tiene_acceso_modulo("hdt")` — puede entrar al programa
- `es_administrador_en_modulo("hdt")` — permisos elevados en ese programa
- `modulos_habilitados()` — lista de modulos para menus

---

## Paso 0 — Prerrequisitos (una sola vez en el ecosistema)

En **Portal-Paldaca** (ya hecho si sigues este repo):

```powershell
cd Portal-Paldaca
.\venv\Scripts\python.exe backend\manage.py migrate
.\venv\Scripts\python.exe backend\manage.py seed_core_modulos
```

En `/admin` del portal:

1. Verificar modulos (`hdt`, `calidad`, `codigos`, `activos`, …).
2. Por cada usuario: asignar **Accesos a modulos** (inline en el usuario).
3. Superuser solo para TI / soporte global.

---

## Paso 1 — Preparar el proyecto satelite

Ejemplo: integrar **core_HDT** en puerto **8001**, codigo de modulo **`hdt`**.

### 1.1 Copiar la app `core`

Desde:

`Portal-Paldaca/backend/core/`

Hacia el satelite (ajusta rutas):

`core_HDT/core/`   ← carpeta de app Django llamada `core`

Archivos minimos necesarios:

```
core/
  __init__.py
  apps.py
  models.py
  admin.py
  middleware.py
  migrations/          # TODAS, en orden
  management/commands/seed_core_modulos.py
```

Opcional en satelite (solo si el portal no esta en el mismo proceso):

- `views.py`, `urls.py`, `views_auth.py`, `serializers.py` — no obligatorios si el login solo ocurre en el portal.

### 1.2 Eliminar o aislar el modelo `Usuario` antiguo

En HDT hoy existe `Usuario` con `Disciplina` y `Perfil` anidados. Plan:

1. Dejar de usar ese modelo como `AUTH_USER_MODEL`.
2. Migrar datos a `core_usuario` (script aparte; ver Paso 6).
3. Renombrar tablas de negocio HDT con prefijo `hdt_` y FK a `core.UsuarioPaldaca`.

**No** mantener dos tablas de usuarios en la misma BD.

---

## Paso 2 — Variables de entorno (`key.env`)

Usa el **mismo** `key.env` en portal y satelites (copia o enlace simbolico).

Plantilla: `Portal-Paldaca/key.env.example`

```env
DJANGO_SECRET_KEY=...                    # IDENTICA en todos los programas
SESSION_COOKIE_NAME=paldaca_sessionid
SESSION_COOKIE_DOMAIN=                     # vacio en local
PALDACA_SSO_LOGIN_URL=http://localhost:5173/login/
MYSQL_DB=paldaca_db
MYSQL_USER=...
MYSQL_PASSWORD=...
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

Produccion:

```env
SESSION_COOKIE_DOMAIN=.cpaldaca.com
PALDACA_SSO_LOGIN_URL=https://www.cpaldaca.com/login/
```

Cargar en settings del satelite igual que el portal:

```python
from dotenv import load_dotenv
load_dotenv(BASE_DIR.parent / "key.env")  # ajustar ruta segun estructura
```

---

## Paso 3 — `settings.py` del satelite

### 3.1 Apps instaladas

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",           # ← app copiada del portal
    "tu_app_hdt",     # app de negocio del programa
]
```

### 3.2 Usuario y base de datos

```python
AUTH_USER_MODEL = "core.UsuarioPaldaca"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_DB", "paldaca_db"),
        # ... mismas credenciales que el portal
    }
}
```

### 3.3 Sesion SSO

```python
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "paldaca_sessionid")
SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN") or None  # vacio en local

PALDACA_SSO_LOGIN_URL = os.getenv(
    "PALDACA_SSO_LOGIN_URL", "http://localhost:5173/login/"
)
PALDACA_STRICT_SESSION_CONSISTENCY = os.getenv(
    "PALDACA_STRICT_SESSION_CONSISTENCY", "true"
)
```

En `development.py` del satelite (igual que el portal):

```python
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_DOMAIN = None
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
```

### 3.4 Middleware (orden importa)

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.middleware.PaldacaSessionMiddleware",  # ← despues de AuthenticationMiddleware
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

---

## Paso 4 — Migraciones en el satelite

Solo la app `core` crea tablas `core_*`. El satelite **no** debe tener migraciones duplicadas de usuario.

```powershell
cd core_HDT
..\Portal-Paldaca\venv\Scripts\python.exe manage.py migrate
# Si core ya migro en el portal contra la misma BD, muchas migraciones diran "No migrations to apply"
```

Si es la primera vez en BD vacia: `migrate` crea todo el esquema `core`.

Comando util (ejecutar en cualquier proyecto con `core`):

```powershell
python manage.py seed_core_modulos
```

---

## Paso 5 — Proteger vistas y login

### 5.1 Quitar login local (o dejarlo solo para emergencias)

En HDT, desactivar o redirigir:

- `path('login/', ...)` → redirigir a `PALDACA_SSO_LOGIN_URL`

Ejemplo:

```python
from django.conf import settings
from django.shortcuts import redirect

def login_redirect(request):
    return redirect(settings.PALDACA_SSO_LOGIN_URL)
```

### 5.2 Decorador / mixin recomendado

Crear en el satelite (ej. `tu_app/decorators.py`):

```python
from functools import wraps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

MODULO_CODIGO = "hdt"  # cambiar por programa: calidad, codigos, activos, etc.


def requiere_modulo_paldaca(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if not user.tiene_acceso_modulo(MODULO_CODIGO):
            if not user.is_authenticated:
                return redirect(settings.PALDACA_SSO_LOGIN_URL)
            return HttpResponseForbidden("No tienes acceso a este programa.")
        return view_func(request, *args, **kwargs)
    return _wrapped
```

Uso:

```python
@requiere_modulo_paldaca
def dashboard(request):
    es_admin = request.user.es_administrador_en_modulo("hdt")
    ...
```

### 5.3 Admin Django del satelite

- `AUTH_USER_MODEL` ya apunta a `core.UsuarioPaldaca`.
- Puedes registrar `core` en admin (viene en `core/admin.py`).
- Usuarios se gestionan preferiblemente desde el **admin del portal** (8000) para centralizar accesos a modulos.

---

## Paso 6 — Migrar datos de usuarios (HDT y legacy)

Antes del cutover, script de migracion (ejecutar una vez):

1. Leer usuarios viejos de HDT (`auth_user` o tabla propia).
2. Crear/actualizar en `core_usuario` (mapear `username` = cedula o email).
3. Guardar tabla de mapeo `hdt_legacy_user_map (old_id, core_usuario_id)`.
4. Actualizar FKs en tablas `hdt_*` para apuntar a `core_usuario.id`.
5. Asignar `UsuarioModulo` para modulo `hdt`.

En `/admin` del portal, para cada usuario migrado:

- Rol: `usuario` o `administrador`
- Accesos a modulos: marcar `hdt` (y otros que correspondan)

---

## Paso 7 — Probar en local

Checklist por satelite:

| # | Prueba | Resultado esperado |
|---|--------|-------------------|
| 1 | Sin login, abrir `http://localhost:8001/` | Redirige a portal login |
| 2 | Login en `http://localhost:5173/login` | Cookie `paldaca_sessionid` en `localhost` |
| 3 | Abrir de nuevo `http://localhost:8001/` | Entra sin pedir password |
| 4 | Usuario sin fila en `core_usuario_modulo` para `hdt` | 403 o mensaje de sin acceso |
| 5 | Usuario con acceso y `rol=administrador` | Entra; `es_administrador_en_modulo("hdt")` True |
| 6 | Quitar acceso en admin y recargar | Sesion invalidada (middleware) o 403 |
| 7 | Superuser | Accede aunque no tenga filas en usuario_modulo |

Comandos:

```powershell
# Portal
cd Portal-Paldaca
.\venv\Scripts\python.exe backend\manage.py runserver 8000

# Frontend
cd Portal-Paldaca\frontend
npm run dev

# Satelite (ej. HDT)
cd core_HDT
..\Portal-Paldaca\venv\Scripts\python.exe manage.py runserver 8001
```

**Siempre `localhost`**, nunca mezclar con `127.0.0.1`.

Mas detalle: [sso-desarrollo-local.md](sso-desarrollo-local.md).

---

## Paso 8 — Mapa codigo de modulo por programa

| Programa | Puerto dev sugerido | `MODULO_CODIGO` | Prefijo tablas negocio |
|----------|---------------------|-----------------|-------------------------|
| Portal | 8000 / 5173 | `portal` | `portal_` |
| Hoja de tiempo (HDT) | 8001 | `hdt` | `hdt_` |
| Calidad | 8002 | `calidad` | `calidad_` o existente |
| Codigos | 8003 | `codigos` | `codigos_` |
| Activos | 8004 | `activos` | `activos_` |

Ajusta puertos segun tu maquina; lo importante es el **`codigo`** en `core_modulo`.

---

## Errores frecuentes

| Sintoma | Causa | Solucion |
|---------|-------|----------|
| Satelite pide login otra vez | `SECRET_KEY` distinta o cookie con dominio `cpaldaca.com` en local | Mismo `key.env`; `SESSION_COOKIE_DOMAIN` vacio |
| Cookie no aparece tras login en 5173 | Frontend sin `credentials: include` | Ya corregido en portal; satelite solo lee cookie |
| `InconsistentMigrationHistory` | Migraciones `core` distintas entre repos | Sincronizar carpeta `core/migrations` |
| Dos tablas de usuarios | No migraste AUTH_USER_MODEL | Un solo `core.UsuarioPaldaca` |
| Admin ve todos los modulos pero HDT dice 403 | Falta fila en `core_usuario_modulo` | Asignar modulo en admin (salvo superuser) |

---

## Prompts para Cursor (copiar en cada repo satelite)

### Prompt 1 — Auditoria inicial

```
Integra este proyecto Django con el SSO de Portal Paldaca siguiendo
docs/guia-integracion-programas-satelite.md del repo Portal-Paldaca.

Codigo de modulo de esta app: hdt
Puerto dev: 8001

1. Lista AUTH_USER_MODEL, INSTALLED_APPS, MIDDLEWARE y DATABASES actuales.
2. Indica si existe modelo Usuario propio y tablas que FK a el.
3. Propone plan de cambios minimos sin romper datos de negocio.
```

### Prompt 2 — Aplicar integracion

```
Copia/ajusta la app core desde Portal-Paldaca/backend/core/.
Configura settings: AUTH_USER_MODEL, SESSION_COOKIE_*, PaldacaSessionMiddleware,
misma BD que key.env del portal.

Crea decorador requiere_modulo_paldaca con MODULO_CODIGO='hdt'.
Redirige login local a PALDACA_SSO_LOGIN_URL.
No dupliques tablas core_* en migraciones del satelite.
```

### Prompt 3 — Migracion de usuarios HDT

```
Genera script de migracion de usuarios del modelo Usuario antiguo de HDT
hacia core.UsuarioPaldaca. Incluye tabla de mapeo old_id->new_id y pasos
para actualizar FKs en tablas hdt_*. Documenta rollback.
```

---

## Relacion con otros documentos

| Documento | Contenido |
|-----------|-----------|
| [plan de accion.md](../plan%20de%20accion.md) | Vision global, BD unificada, roadmap |
| [sso-desarrollo-local.md](sso-desarrollo-local.md) | Cookies, puertos, pruebas SSO |
| [key.env.example](../key.env.example) | Variables de entorno |
| [README.md](../README.md) | Arranque del portal |

---

## Resumen ejecutivo

1. **Si, copia `backend/core/`** a cada satelite (misma BD, mismas migraciones).
2. **Portal** = unico login (React + `auth.login` + cookie).
3. **Satelites** = `AUTH_USER_MODEL` + middleware + `tiene_acceso_modulo("<codigo>")`.
4. **Asignacion de modulos** en `/admin` del portal (`core_usuario_modulo`).
5. **Superuser** = unico rol con acceso global sin asignacion manual.

Cuando termines un satelite, marca en `plan de accion.md` el checklist de la seccion 4.
