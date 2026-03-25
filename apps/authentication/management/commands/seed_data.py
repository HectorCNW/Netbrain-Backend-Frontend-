"""
python manage.py seed_data

Crea usuarios de prueba, un proyecto de ejemplo completo con páginas,
notas importantes, preguntas y respuestas.
"""
from django.core.management.base import BaseCommand
from apps.authentication.models import User
from apps.projects.models import ProyectoWiki, ColaboradorProyecto, ActividadProyecto
from apps.pages.models import PaginaWiki, VersionPaginaWiki
from apps.qa.models import PreguntaProyecto, RespuestaProyecto
from apps.important_notes.models import NotaImportanteProyecto


class Command(BaseCommand):
    help = "Crea datos de prueba: usuarios, proyectos, páginas, notas y Q&A"

    def handle(self, *args, **options):
        self.stdout.write("🌱  Generando datos de prueba para NetBrain...\n")

        # ── Usuarios ──────────────────────────────────────────────────────────
        admin, _ = User.objects.get_or_create(
            email="admin@netbrain.dev",
            defaults={"nombre": "Admin NetBrain", "rol": User.ROL_ADMIN, "is_staff": True, "is_superuser": True},
        )
        admin.set_password("Admin1234!")
        admin.save()

        editor, _ = User.objects.get_or_create(
            email="editor@netbrain.dev",
            defaults={"nombre": "Editor Demo", "rol": User.ROL_EDITOR},
        )
        editor.set_password("Editor1234!")
        editor.save()

        viewer, _ = User.objects.get_or_create(
            email="viewer@netbrain.dev",
            defaults={"nombre": "Viewer Demo", "rol": User.ROL_VIEWER},
        )
        viewer.set_password("Viewer1234!")
        viewer.save()

        self.stdout.write(self.style.SUCCESS("  ✓ Usuarios creados"))

        # ── Proyecto ──────────────────────────────────────────────────────────
        proyecto, creado = ProyectoWiki.objects.get_or_create(
            nombre="Portal E-Commerce",
            defaults={
                "descripcion": "Plataforma de comercio electrónico con microservicios.",
                "owner": admin,
                "lenguajes": ["TypeScript", "Python", "SQL", "Docker"],
                "repositorios": ["https://github.com/demo/ecommerce-frontend", "https://github.com/demo/ecommerce-api"],
                "estado": "activo",
            },
        )

        ColaboradorProyecto.objects.get_or_create(proyecto=proyecto, usuario=admin, defaults={"rol_en_proyecto": "owner"})
        ColaboradorProyecto.objects.get_or_create(proyecto=proyecto, usuario=editor, defaults={"rol_en_proyecto": "editor"})
        ColaboradorProyecto.objects.get_or_create(proyecto=proyecto, usuario=viewer, defaults={"rol_en_proyecto": "viewer"})

        if creado:
            ActividadProyecto.objects.create(proyecto=proyecto, usuario=admin, tipo_evento="proyecto_creado", entidad="proyecto", entidad_id=proyecto.id)

        self.stdout.write(self.style.SUCCESS("  ✓ Proyecto creado"))

        # ── Páginas ───────────────────────────────────────────────────────────
        paginas_data = [
            {
                "titulo": "Arquitectura General",
                "slug": "arquitectura-general",
                "contenido_markdown": """# Arquitectura General

## Resumen
El sistema usa una arquitectura de **microservicios** con los siguientes componentes principales:

- **Frontend** — React SPA alojado en Vercel
- **API Gateway** — Kong como proxy inverso
- **Servicios** — Python/Django independientes por dominio
- **Base de datos** — PostgreSQL por servicio (patrón Database-per-Service)
- **Mensajería** — RabbitMQ para eventos asincrónicos

## Diagrama de componentes

```
[React SPA] → [API Gateway / Kong] → [Auth Service]
                                   → [Product Service]
                                   → [Order Service]
                                   → [Notification Service]
```

## Principios de diseño
1. Cada servicio es desplegable de forma independiente.
2. La comunicación síncrona es REST; la asíncrona es por eventos.
3. No hay base de datos compartida entre servicios.
""",
                "tags": ["arquitectura", "backend", "infra"],
            },
            {
                "titulo": "Setup Local",
                "slug": "setup-local",
                "contenido_markdown": """# Setup Local

## Requisitos previos
- Docker 24+
- Node.js 20+
- Python 3.11+
- PostgreSQL 15+

## Pasos

### 1. Clonar repositorios
```bash
git clone https://github.com/demo/ecommerce-frontend
git clone https://github.com/demo/ecommerce-api
```

### 2. Variables de entorno
```bash
cp .env.example .env
# Editar según entorno local
```

### 3. Levantar con Docker Compose
```bash
docker compose up -d
```

### 4. Ejecutar migraciones
```bash
docker compose exec api python manage.py migrate
docker compose exec api python manage.py seed_data
```

### 5. Frontend
```bash
cd ecommerce-frontend
npm install
npm run dev
```

La app estará disponible en `http://localhost:3000`.
""",
                "tags": ["setup", "docker", "local"],
            },
            {
                "titulo": "API — Referencia de Endpoints",
                "slug": "api-endpoints",
                "contenido_markdown": """# API — Referencia de Endpoints

## Autenticación
Todos los endpoints (salvo login/register) requieren `Authorization: Bearer <token>`.

## Productos

| Método | Ruta                  | Descripción              |
|--------|-----------------------|--------------------------|
| GET    | /api/products         | Listar productos         |
| POST   | /api/products         | Crear producto           |
| GET    | /api/products/{id}    | Detalle                  |
| PATCH  | /api/products/{id}    | Actualizar               |
| DELETE | /api/products/{id}    | Archivar                 |

## Pedidos

| Método | Ruta                  | Descripción              |
|--------|-----------------------|--------------------------|
| POST   | /api/orders           | Crear pedido             |
| GET    | /api/orders/{id}      | Estado del pedido        |
| POST   | /api/orders/{id}/cancel | Cancelar               |

## Respuestas de error

```json
{
  "error": "Descripción del error",
  "code": "ERROR_CODE",
  "detalles": {}
}
```
""",
                "tags": ["api", "endpoints", "backend"],
            },
        ]

        for pd in paginas_data:
            pagina, p_creada = PaginaWiki.objects.get_or_create(
                proyecto=proyecto,
                slug=pd["slug"],
                defaults={
                    "titulo": pd["titulo"],
                    "contenido_markdown": pd["contenido_markdown"],
                    "tags": pd["tags"],
                    "creado_por": admin,
                    "ultima_edicion_por": editor,
                    "version_actual": 1,
                },
            )
            if p_creada:
                VersionPaginaWiki.objects.create(
                    pagina=pagina,
                    numero_version=1,
                    contenido_markdown=pagina.contenido_markdown,
                    editado_por=admin,
                    mensaje_cambio="Versión inicial",
                )

        self.stdout.write(self.style.SUCCESS("  ✓ Páginas creadas"))

        # ── Notas importantes ────────────────────────────────────────────────
        notas_data = [
            {
                "tipo": "no_tocar",
                "titulo": "NO modificar tabla `orders` sin migración revisada",
                "contenido_markdown": "La tabla `orders` tiene triggers en PostgreSQL que sincronizan estados. Cualquier cambio de esquema **debe revisarse con el equipo de backend** antes de deployar.",
                "prioridad": "alta",
            },
            {
                "tipo": "funcion_clave",
                "titulo": "recalculate_inventory() — función crítica de stock",
                "contenido_markdown": "Esta función recalcula el inventario en tiempo real. Se llama en cada confirmación de pedido. No cambiar su firma sin actualizar todos los consumers de RabbitMQ.",
                "prioridad": "alta",
            },
            {
                "tipo": "decision_arquitectura",
                "titulo": "Decisión: PostgreSQL por servicio (no MongoDB)",
                "contenido_markdown": "Se evaluó MongoDB para el catálogo de productos pero se descartó por la necesidad de transacciones ACID en el flujo de pedidos. Ver ADR-004.",
                "prioridad": "media",
            },
            {
                "tipo": "riesgo",
                "titulo": "Riesgo: timeout en integración con pasarela de pago",
                "contenido_markdown": "La pasarela de pago externa tiene SLA de 99.5%. En caso de caída, los pedidos quedan en estado `pending_payment`. Hay un job nocturno que los reintenta.",
                "prioridad": "alta",
            },
        ]

        for nd in notas_data:
            NotaImportanteProyecto.objects.get_or_create(
                proyecto=proyecto,
                titulo=nd["titulo"],
                defaults={**nd, "creado_por": admin},
            )

        self.stdout.write(self.style.SUCCESS("  ✓ Notas importantes creadas"))

        # ── Preguntas y respuestas ────────────────────────────────────────────
        pregunta, _ = PreguntaProyecto.objects.get_or_create(
            proyecto=proyecto,
            titulo="¿Cómo se gestiona la caché de productos?",
            defaults={
                "pregunta": "Quiero saber si existe una capa de caché para las llamadas a `/api/products` y cómo invalidarla cuando se actualiza un producto.",
                "creado_por": viewer,
                "estado": "resuelta",
                "tags": ["api", "cache", "performance"],
            },
        )

        respuesta, _ = RespuestaProyecto.objects.get_or_create(
            pregunta=pregunta,
            creado_por=editor,
            defaults={
                "respuesta": "Sí, usamos Redis con TTL de 5 minutos. La invalidación ocurre automáticamente a través del signal `post_save` del modelo `Product`. Puedes forzar invalidación manual con `python manage.py clear_product_cache --id <id>`.",
                "es_aceptada": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("  ✓ Q&A creada"))
        self.stdout.write(self.style.SUCCESS("\n✅  Seed completado. Usuarios disponibles:"))
        self.stdout.write("   admin@netbrain.dev  / Admin1234!")
        self.stdout.write("   editor@netbrain.dev / Editor1234!")
        self.stdout.write("   viewer@netbrain.dev / Viewer1234!")
