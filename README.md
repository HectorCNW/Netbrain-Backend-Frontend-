# NetBrain — Backend (Django + DRF)

## Arquitectura

```
netbrain_backend/
├── manage.py
├── requirements.txt
├── .env.example
├── config/
│   └── settings/
│       ├── base.py
│       ├── development.py
│       └── production.py
├── netbrain/
│   ├── urls.py
│   └── wsgi.py
└── apps/
    ├── authentication/      # JWT, registro, login
    ├── projects/            # Proyectos Wiki + colaboradores + actividad
    ├── pages/               # Páginas + versionado
    ├── github_integration/  # PRs, sync con GitHub API
    ├── qa/                  # Preguntas y respuestas
    ├── important_notes/     # Notas críticas del proyecto
    ├── documents/           # Subida de archivos PDF/MD
    ├── search/              # Búsqueda global
    └── exports/             # Exportación PDF
```

## Setup local

### 1. Clonar y crear entorno virtual
```bash
git clone <repo>
cd netbrain_backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 3. Base de datos PostgreSQL
```bash
createdb netbrain_db
python manage.py migrate
python manage.py createsuperuser
```

### 4. Seed de datos de prueba
```bash
python manage.py seed_users       # Crea usuarios admin, editor, viewer
python manage.py seed_projects    # Crea proyectos de ejemplo
```

### 5. Ejecutar servidor
```bash
python manage.py runserver
```

## Variables de entorno (.env)

```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:pass@localhost:5432/netbrain_db
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
JWT_ACCESS_TOKEN_LIFETIME=60       # minutos
JWT_REFRESH_TOKEN_LIFETIME=7       # días
MEDIA_ROOT=media/
PDF_EXPORT_DIR=exports/
```

## Usuarios de prueba

| Email                  | Password    | Rol    |
|------------------------|-------------|--------|
| admin@netbrain.dev     | Admin1234!  | admin  |
| editor@netbrain.dev    | Editor1234! | editor |
| viewer@netbrain.dev    | Viewer1234! | viewer |

## Endpoints principales

```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh

GET    /api/proyectos
POST   /api/proyectos
GET    /api/proyectos/{id}
PATCH  /api/proyectos/{id}
DELETE /api/proyectos/{id}

GET    /api/proyectos/{id}/paginas
POST   /api/proyectos/{id}/paginas
GET    /api/paginas/{id}
PATCH  /api/paginas/{id}
DELETE /api/paginas/{id}

GET    /api/paginas/{id}/versiones
GET    /api/paginas/{id}/versiones/{version}
POST   /api/paginas/{id}/restaurar/{version}
GET    /api/paginas/{id}/exportar.pdf

GET    /api/proyectos/{id}/github/prs
POST   /api/proyectos/{id}/github/conectar
POST   /api/proyectos/{id}/github/sync
GET    /api/proyectos/{id}/github/resumen

GET    /api/proyectos/{id}/preguntas
POST   /api/proyectos/{id}/preguntas
GET    /api/preguntas/{id}
POST   /api/preguntas/{id}/respuestas
PATCH  /api/preguntas/{id}/resolver

GET    /api/proyectos/{id}/notas-importantes
POST   /api/proyectos/{id}/notas-importantes
PATCH  /api/notas-importantes/{id}
DELETE /api/notas-importantes/{id}

GET    /api/proyectos/{id}/documentos
POST   /api/proyectos/{id}/documentos
DELETE /api/documentos/{id}

GET    /api/proyectos/{id}/actividad
GET    /api/proyectos/{id}/exportar.pdf

GET    /api/buscar?q=...&proyectoId=&lenguaje=&autor=&tag=&fechaDesde=&fechaHasta=
```
