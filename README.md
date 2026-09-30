# ObraClik
# 🛠️ ObraClik - Plataforma de Servicios Técnicos y Profesionales

**ObraClik** es una plataforma web desarrollada en Flask que conecta a usuarios con especialistas, técnicos y profesionales del sector de la construcción, mantenimiento y servicios para el hogar.

**Características Principales**
Gestión de Usuarios y Perfiles: Registro, inicio de sesión y administración de perfiles detallados de clientes y profesionales.
Catálogo de Servicios: Visualización de servicios disponibles con filtros e interfaz responsiva.
Flujo de Pedidos y Carrito: Módulo para la selección de servicios, gestión de carrito y confirmación de solicitudes.
Panel Administrativo: Scripts y herramientas para actualizar y gestionar roles/administradores (actualizar_admin.py).
**Tecnologías Utilizadas**
**Backend:** Python 3, Flask
**Frontend:** HTML5, CSS3, JavaScript (Jinja2 Templates)
**Base de Datos:** MySQL / SQLite
**Entorno Virtual:** Virtualenv (.venv / env)
**Estructura del Proyecto**
ObraClik/
├── ObraClikweb/
│   ├── .venv/                 # Entorno virtual
│   ├── static/                # Archivos estáticos (CSS, JS, Imágenes)
│   │   └── uploads/           # Recursos subidos por usuarios
│   ├── templates/             # Plantillas HTML (Jinja2)
│   │   ├── base.html          # Estructura principal
│   │   ├── index.html         # Página de inicio
│   │   ├── login.html         # Inicio de sesión
│   │   ├── registro.html      # Registro de usuarios
│   │   ├── servicios.html     # Catálogo de servicios
│   │   ├── carrito.html       # Carrito de pedidos
│   │   ├── confirmacion.html  # Confirmación de solicitud
│   │   ├── perfil.html        # Vista general de perfil
│   │   ├── perfil_detalle.html# Detalle y edición de perfil
│   │   ├── pedidos.html       # Historial de pedidos
│   │   ├── nosotros.html      # Información institucional
│   │   └── crecimiento.html   # Estadísticas / Crecimiento
│   ├── app.py                 # Aplicación principal Flask (Rutas y lógica)
│   └── actualizar_admin.py   # Script auxiliar de administración
└── README.md                  # Documentación del repositorio
